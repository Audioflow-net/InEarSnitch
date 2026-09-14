import re

with open('main.py', 'r') as f:
    content = f.read()

optimized_worker = """    def run(self):
        import sounddevice as sd
        import numpy as np
        from scipy import interpolate
        
        # Precompute Pink Noise Buffer (4 seconds to avoid obvious repeating patterns)
        N_noise = self.fs * 4
        X_white = np.fft.rfft(np.random.randn(N_noise))
        S = np.sqrt(np.arange(X_white.size) + 1.0)
        y = np.fft.irfft(X_white / S, n=N_noise)
        pink_noise_full = (y / np.max(np.abs(y))) * 0.15
        self.noise_idx = 0
        
        # Precompute frequencies and calibration curve
        freqs = np.fft.rfftfreq(self.blocksize, 1/self.fs)
        cal_offset = np.zeros_like(freqs)
        if self.cal_f is not None and self.cal_m is not None:
            interp_func = interpolate.interp1d(self.cal_f, self.cal_m, bounds_error=False, fill_value=0.0)
            cal_offset = interp_func(freqs)
            
        # Precompute Hanning window
        window = np.hanning(self.blocksize)

        def callback(indata, outdata, frames, time, status):
            if not self.running:
                raise sd.CallbackStop
            try:
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
                    
                if self.target_channel == "Left":
                    outdata[:, 0] = pn
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = 0.0
                else:
                    outdata[:, 0] = 0.0
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = pn
                    
                sig = indata[:, 0].copy()
                sig_w = sig * window
                
                mag = np.abs(np.fft.rfft(sig_w))
                # Simple smoothing
                kernel_size = 15
                kernel = np.ones(kernel_size) / kernel_size
                mag_smooth = np.convolve(mag, kernel, mode='same')
                
                mag_db = 20 * np.log10(mag_smooth + 1e-12)
                mag_db += cal_offset
                    
                self.update_signal.emit(freqs, mag_db)
            except Exception as e:
                print(f"[LiveSealWorker Error] {e}")
                self.error.emit(str(e))
                raise sd.CallbackAbort

        try:
            with sd.Stream(device=(self.in_idx, self.out_idx),
                           samplerate=self.fs, blocksize=self.blocksize,
                           channels=(1, 2), callback=callback):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            import traceback
            traceback.print_exc()"""

content = re.sub(
    r'    def run\(self\):.*?traceback\.print_exc\(\)  # Prints to stderr, which LogStream catches!',
    optimized_worker,
    content,
    flags=re.DOTALL
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
