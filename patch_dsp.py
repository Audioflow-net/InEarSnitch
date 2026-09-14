import sys

# --- PATCH AUDIO ENGINE ---
with open('audio_engine.py', 'r') as f:
    ae = f.read()

old_measure_sig = """def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=5.0, f_end=24000.0, mic_cal_freqs=None, mic_cal_mags=None, progress_callback=None):"""
new_measure_sig = """def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=5.0, f_end=24000.0, mic_cal_freqs=None, mic_cal_mags=None, spl_offset_db=0.0, progress_callback=None):"""
ae = ae.replace(old_measure_sig, new_measure_sig)

old_fft = """        N = len(ir)
        peak_idx = np.argmax(np.abs(ir))
        
        # Window: -10ms to +100ms (100ms resolves down to 10Hz, completely capturing IEM bass)
        win_pre = int(0.01 * self.sample_rate)
        win_post = int(0.10 * self.sample_rate)
        w_start = max(0, peak_idx - win_pre)
        w_end = min(N, peak_idx + win_post)
        
        # Apply a Tukey-like window (flat in middle, Hann tapered at edges)
        from scipy.signal.windows import hann
        import numpy as np
        taper_len = int(0.005 * self.sample_rate) # 5ms taper
        window = np.ones(w_end - w_start)
        if len(window) > 2 * taper_len:
            window[:taper_len] = hann(taper_len * 2)[:taper_len]
            window[-taper_len:] = hann(taper_len * 2)[taper_len:]
            
        ir_windowed = np.zeros_like(ir)
        ir_windowed[w_start:w_end] = ir[w_start:w_end] * window
        
        freqs = rfftfreq(N, 1 / self.sample_rate)
        
        # WISSENSCHAFTLICHES UPDATE: Time Alignment (Zero-Phase Reference)
        # We circularly shift the IR so the peak is exactly at t=0.
        # This completely eliminates random USB latency from the phase response
        # and allows mathematically perfect L/R phase comparisons.
        ir_shifted = np.roll(ir_windowed, -peak_idx)
        fft_res = rfft(ir_shifted)
        
        # Calculate Magnitude (dB SPL representation)
        # Adding an arbitrary +100 dB offset so uncalibrated digital values 
        # sit in a typical acoustic SPL range (e.g. 80-110 dB) instead of negative.
        mag = 20 * np.log10(np.abs(fft_res) + 1e-12) + 100"""

new_fft = """        N = len(ir)
        
        # PRO-AUDIO UPDATE: Onset detection (5% threshold of peak)
        # We align to the onset to preserve real physical group delay (Time of Flight).
        import numpy as np
        peak_amp_ir = np.max(np.abs(ir))
        threshold = 0.05 * peak_amp_ir
        onset_indices = np.where(np.abs(ir) > threshold)[0]
        onset_idx = onset_indices[0] if len(onset_indices) > 0 else np.argmax(np.abs(ir))
        
        # Window: -5ms before onset to +300ms after onset (perfectly captures sub-bass without cutting group delay)
        win_pre = int(0.005 * self.sample_rate)
        win_post = int(0.3 * self.sample_rate)
        w_start = max(0, onset_idx - win_pre)
        w_end = min(N, onset_idx + win_post)
        
        # Apply a Tukey-like window (flat in middle, Hann tapered at edges)
        from scipy.signal.windows import hann
        taper_len = int(0.005 * self.sample_rate) # 5ms taper
        window = np.ones(w_end - w_start)
        if len(window) > 2 * taper_len:
            window[:taper_len] = hann(taper_len * 2)[:taper_len]
            window[-taper_len:] = hann(taper_len * 2)[taper_len:]
            
        ir_windowed = np.zeros_like(ir)
        ir_windowed[w_start:w_end] = ir[w_start:w_end] * window
        
        freqs = rfftfreq(N, 1 / self.sample_rate)
        
        # PRO-AUDIO UPDATE: Time Alignment (Zero-Phase Reference)
        # Shift IR so the ONSET is exactly at t=0. This removes random USB latency
        # but preserves the physical acoustic latency between onset and HF peak.
        ir_shifted = np.roll(ir_windowed, -onset_idx)
        fft_res = rfft(ir_shifted)
        
        # Calculate Magnitude (dB SPL representation) using calibrated user offset
        mag = 20 * np.log10(np.abs(fft_res) + 1e-12) + spl_offset_db"""
ae = ae.replace(old_fft, new_fft)

with open('audio_engine.py', 'w') as f:
    f.write(ae)

# --- PATCH MAIN ---
with open('main.py', 'r') as f:
    main_code = f.read()

old_worker_init = """    def __init__(self, audio_engine, in_idx, out_idx, target_channel, cal_f=None, cal_m=None, sweeps=1):
        super().__init__()
        self.audio_engine = audio_engine
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.target_channel = target_channel
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.sweeps = sweeps"""

new_worker_init = """    def __init__(self, audio_engine, in_idx, out_idx, target_channel, cal_f=None, cal_m=None, sweeps=1, spl_offset_db=0.0):
        super().__init__()
        self.audio_engine = audio_engine
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.target_channel = target_channel
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.sweeps = sweeps
        self.spl_offset_db = spl_offset_db"""
main_code = main_code.replace(old_worker_init, new_worker_init)

old_worker_call = """                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f,
                                                mic_cal_mags=self.cal_m,
                                                progress_callback=lambda t, s=i+1: self.sweep_progress.emit(t, s))"""

new_worker_call = """                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f,
                                                mic_cal_mags=self.cal_m,
                                                spl_offset_db=self.spl_offset_db,
                                                progress_callback=lambda t, s=i+1: self.sweep_progress.emit(t, s))"""
main_code = main_code.replace(old_worker_call, new_worker_call)

old_instantiate = """        self.worker = MeasurementWorker(self.audio_engine, self.selected_in_idx, self.selected_out_idx, target_ch, cal_f, cal_m, sweeps)"""
new_instantiate = """        spl = getattr(self, 'spl_offset_db', 0.0)
        self.worker = MeasurementWorker(self.audio_engine, self.selected_in_idx, self.selected_out_idx, target_ch, cal_f, cal_m, sweeps, spl)"""
main_code = main_code.replace(old_instantiate, new_instantiate)

with open('main.py', 'w') as f:
    f.write(main_code)
