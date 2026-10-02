class LiveSealWorker(QThread):

    update_signal = Signal(object, object)
    error = Signal(str)

    def __init__(self, in_idx, out_idx, cal_f=None, cal_m=None, target_channel="Left"):
        super().__init__()
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.target_channel = target_channel
        self.running = True
        self.fs = 48000
        self.blocksize = 16384

    def set_target_channel(self, target_channel):
        self.target_channel = target_channel

    def run(self):
        import sounddevice as sd
        import numpy as np
        from scipy import interpolate
        
        # Precompute Pink Noise Buffer (4 seconds to avoid obvious repeating patterns)
        N_noise = self.fs * 4
        X_white = np.fft.rfft(np.random.randn(N_noise))
        S = np.sqrt(np.arange(X_white.size) + 1.0)
        y = np.fft.irfft(X_white / S, n=N_noise)
        # Use calibrated amplitude if available, otherwise 0.15
        cal_amp = getattr(self, '_cal_amp', 0.15)
        pink_noise_full = (y / np.max(np.abs(y))) * cal_amp
        self.noise_idx = 0
        
        # Precompute frequencies and calibration curve
        freqs = np.fft.rfftfreq(self.blocksize, 1/self.fs)
        
        # Precompute Logarithmic Binning Matrix
        import math
        f_min = 20.0
        f_max = 24000.0
        octave_frac = 1.0 / 48.0
        n_bins = int(math.log2(f_max / f_min) / octave_frac) + 1
        log_freqs = f_min * (2.0 ** (np.arange(n_bins) * octave_frac))
        
        M = np.zeros((n_bins, len(freqs)))
        for i in range(n_bins):
            f_center = log_freqs[i]
            f_low = f_center * (2.0 ** (-octave_frac / 2.0))
            f_high = f_center * (2.0 ** (octave_frac / 2.0))
            mask = (freqs >= f_low) & (freqs < f_high)
            if np.any(mask):
                M[i, mask] = 1.0 / np.sum(mask)
            else:
                idx1 = np.searchsorted(freqs, f_center) - 1
                if idx1 < 0:
                    M[i, 0] = 1.0
                elif idx1 >= len(freqs) - 1:
                    M[i, -1] = 1.0
                else:
                    idx2 = idx1 + 1
                    f1 = freqs[idx1]
                    f2 = freqs[idx2]
                    w2 = (f_center - f1) / (f2 - f1)
                    w1 = 1.0 - w2
                    M[i, idx1] = w1
                    M[i, idx2] = w2
                
        from scipy import sparse
        M_sparse = sparse.csr_matrix(M)
                
        cal_offset = np.zeros_like(log_freqs)
        if self.cal_f is not None and self.cal_m is not None:
            # Logarithmic interpolation for calibration
            safe_log_freqs = np.clip(log_freqs, 1e-6, None)
            safe_cal_f = np.clip(self.cal_f, 1e-6, None)
            cal_offset = np.interp(np.log10(safe_log_freqs), np.log10(safe_cal_f), self.cal_m)
            
        # Precompute Hanning window
        window = np.hanning(self.blocksize)
        in_circ = np.zeros(self.blocksize)
        
        # Precompute Kill-Switch variables (cache to avoid allocations in stream)
        kill_window = None
        kill_high_mask = None
        kill_sig = None

        def callback(indata, outdata, frames, time, status):
            nonlocal in_circ, kill_window, kill_high_mask, kill_sig
            if not self.running:
                raise sd.CallbackStop
            try:
                # EMERGENCY KILL-SWITCH (> 1 kHz)
                if kill_window is None or len(kill_window) != frames:
                    kill_window = np.hanning(frames)
                    kill_freqs = np.fft.rfftfreq(frames, 1/self.fs)
                    kill_high_mask = kill_freqs > 1000.0
                    kill_sig = np.empty(frames, dtype=indata.dtype)
                    
                np.multiply(indata[:, 0], kill_window, out=kill_sig)
                kill_fft = np.fft.rfft(kill_sig)
                
                # Zero-allocation high-frequency energy power (RMS approximated) using vdot
                high_bins = kill_fft[kill_high_mask]
                high_power = np.vdot(high_bins, high_bins).real / (frames**2) * 5.33333
                
                if high_power > 1e-12:
                    if (10 * np.log10(high_power)) > -10.0:
                        self.error.emit("EMERGENCY STOP: Signal zu laut! In-Ear in Gefahr. Bitte Interface leiser drehen.")
                        outdata.fill(0.0) # Prevent loud click on final buffer
                        raise sd.CallbackStop

                # Grab a chunk of precomputed pink noise
                end_idx = self.noise_idx + frames
                if end_idx <= N_noise:
                    pn = pink_noise_full[self.noise_idx:end_idx].copy()
                    self.noise_idx = end_idx
                else:
                    # Wrap around
                    pn = np.empty(frames)
                    rem = N_noise - self.noise_idx
                    pn[:rem] = pink_noise_full[self.noise_idx:]
                    pn[rem:] = pink_noise_full[:frames-rem]
                    self.noise_idx = frames - rem
                
                # Apply Hardware DSP if enabled
                from eq_math import dsp_engine
                if dsp_engine.master_enabled:
                    pn = dsp_engine.process(pn, self.fs)
                    
                pn = np.clip(pn, -cal_amp, cal_amp)
                    
                if self.target_channel == "Left":
                    outdata[:, 0] = pn
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = 0.0
                else:
                    outdata[:, 0] = 0.0
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = pn
                    
                sig = indata[:, 0].copy()
                n_new = len(sig)
                
                if n_new >= self.blocksize:
                    in_circ[:] = sig[-self.blocksize:]
                else:
                    in_circ = np.roll(in_circ, -n_new)
                    in_circ[-n_new:] = sig
                
                sig_w = in_circ * window
                N_sig = self.blocksize
                
                # Normalize the FFT so it outputs true linear amplitude (true dBFS)
                # instead of being artificially inflated by N/2
                mag = np.abs(np.fft.rfft(sig_w)) / (N_sig / 2.0)
                
                # Fast fractional octave log-binning
                mag_smooth = M_sparse @ mag
                
                mag_db = 20 * np.log10(mag_smooth + 1e-12)
                mag_db_out = mag_db + cal_offset
                
                self.update_signal.emit(log_freqs, mag_db_out)
            except sd.CallbackStop:
                raise
            except Exception as e:
                print(f"[LiveSealWorker Error] {e}")
                self.error.emit(str(e))
                raise sd.CallbackAbort

        try:
            with sd.Stream(device=(self.in_idx, self.out_idx),
                           samplerate=self.fs, blocksize=2048,
                           channels=(1, 2), callback=callback):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
            
    def stop(self):
        self.running = False

class MeasurementWorker(QThread):
