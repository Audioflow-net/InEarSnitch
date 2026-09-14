import numpy as np
import sounddevice as sd
from scipy.signal import chirp, fftconvolve
from scipy.fft import rfft, rfftfreq

class AudioEngine:
    def __init__(self, sample_rate=48000, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

    def get_devices(self):
        """Returns all available CoreAudio devices via sounddevice."""
        return sd.query_devices()

    def generate_sweep(self, duration=2.0, f_start=5.0, f_end=24000.0, amplitude=None):
        """Generates a logarithmic sine sweep with fade-in and fade-out.
        
        Args:
            amplitude: Output amplitude (0.0-0.25). Defaults to calibrated value or 0.1.
                       Hard-capped at 0.25 (-12 dBFS) for IEM safety.
        """
        if amplitude is None:
            amplitude = getattr(self, 'calibrated_sweep_amp', 0.1)
        amplitude = min(amplitude, 0.25)  # Absolute safety ceiling
        
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        sweep = chirp(t, f0=f_start, f1=f_end, t1=duration, method='logarithmic')
        
        # Fade in / Fade out to prevent clicks (10ms to preserve full 20Hz-20kHz bandwidth)
        fade_len = int(0.01 * self.sample_rate)
        window = np.ones_like(sweep)
        window[:fade_len] = np.linspace(0, 1, fade_len)
        window[-fade_len:] = np.linspace(1, 0, fade_len)
        
        sweep = sweep * window * amplitude
        # Apply Hardware DSP if enabled
        from eq_math import dsp_engine
        if dsp_engine.master_enabled:
            sweep = dsp_engine.process(sweep, self.sample_rate)
            # SAFETY: Re-apply amplitude ceiling AFTER DSP processing.
            # Without this, a +12 dB EQ boost could push the signal to 4x
            # the intended amplitude, potentially over-excursing BA drivers.
            sweep = np.clip(sweep, -amplitude, amplitude)
            
        return sweep, t

    def get_inverse_filter(self, sweep, duration, f_start=5.0, f_end=24000.0):
        """Generates the inverse filter using Farina's amplitude modulation method."""
        t = np.linspace(0, duration, len(sweep), False)
        amplitude_modulation = np.exp(-t * np.log(f_end / f_start) / duration)
        inverse_sweep = sweep[::-1] * amplitude_modulation
        return inverse_sweep

    def preflight_check(self, input_device_idx, output_device_idx, target_channel='L', amplitude=None):
        """Pre-flight level check: plays a 100ms 1kHz probe tone and measures recording peak.
        
        Returns:
            tuple: (passed: bool, peak_dbfs: float, message: str)
        """
        if amplitude is None:
            amplitude = getattr(self, 'calibrated_sweep_amp', 0.1)
        # Probe tone at HALF the sweep amplitude (sine peaks higher than a spread sweep)
        probe_amp = min(amplitude * 0.5, 0.125)
        
        duration = 0.1  # 100ms probe tone
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, False)
        tone = np.sin(2 * np.pi * 1000 * t) * probe_amp
        
        # Fade to prevent clicks
        fade = int(0.005 * self.sample_rate)
        tone[:fade] *= np.linspace(0, 1, fade)
        tone[-fade:] *= np.linspace(1, 0, fade)
        
        # Route to correct channel (stereo output)
        tone_stereo = np.zeros((n_samples, 2))
        if target_channel == 'L':
            tone_stereo[:, 0] = tone
        else:
            tone_stereo[:, 1] = tone
        
        try:
            # Use same macOS-compatible approach as measure()
            try:
                rec = sd.playrec(tone_stereo, samplerate=self.sample_rate, channels=1,
                                 device=(input_device_idx, output_device_idx), blocking=True)
            except sd.PortAudioError:
                in_chans = sd.query_devices(input_device_idx)['max_input_channels']
                rec = sd.playrec(tone_stereo, samplerate=self.sample_rate, channels=in_chans,
                                 device=(input_device_idx, output_device_idx), blocking=True)
                rec = rec[:, 0:1]
            sd.wait()
        except Exception as e:
            return True, -999.0, f"Pre-flight skipped: {e}"
        
        peak_amp = np.max(np.abs(rec))
        peak_dbfs = 20 * np.log10(peak_amp + 1e-12)
        
        # Only block on actual clipping (> -1 dBFS at half amplitude = guaranteed clip at full)
        if peak_dbfs > -1.0:
            return False, peak_dbfs, "Recording is clipping! Lower your system volume."
        
        if peak_dbfs < -55.0:
            return False, peak_dbfs, "No signal detected. Check IEM connection and system volume."
        
        # Check drift: scale expected peak by the ratio of probe amp to calibrated sweep amp
        cal_rec_peak = getattr(self, 'calibration_rec_peak', None)
        cal_sweep_amp = getattr(self, 'calibrated_sweep_amp', None)
        if cal_rec_peak is not None and cal_sweep_amp is not None:
            # Expected probe peak = cal peak + 20*log10(probe_amp / cal_sweep_amp)
            expected_probe_peak = cal_rec_peak + 20 * np.log10(probe_amp / cal_sweep_amp + 1e-12)
            drift = abs(peak_dbfs - expected_probe_peak)
            if drift > 4.0:
                return False, peak_dbfs, (
                    f"Level shifted by {drift:.0f} dB since calibration "
                    f"(expected {expected_probe_peak:.0f}, got {peak_dbfs:.0f} dBFS). "
                    f"System volume was changed. Re-calibrate or restore volume."
                )
        
        return True, peak_dbfs, f"Level OK ({peak_dbfs:.0f} dBFS)"

    def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=5.0, f_end=24000.0, mic_cal_freqs=None, mic_cal_mags=None, spl_offset_db=0.0, progress_callback=None, amplitude=None):
        """
        Executes a single-ear sweep measurement.
        """
        # 1. Generate stimulus and inverse filter
        sweep, _ = self.generate_sweep(duration, f_start, f_end, amplitude=amplitude)
        inv_sweep = self.get_inverse_filter(sweep, duration, f_start, f_end)
        
        # FIX HF CUTOFF: Add 0.5s of silence at the end of the playback array!
        # If we don't zero-pad, sd.playrec stops recording the exact millisecond the 1s sweep 
        # is done outputting. But because of USB round-trip latency, the highest frequencies 
        # (which sit at the very end of the sweep) haven't reached the microphone yet! 
        # This truncates the HF and causes the graph to drop off a cliff above 10kHz.
        padding_samples = int(0.5 * self.sample_rate)
        sweep_stereo = np.zeros((len(sweep) + padding_samples, 2))
        if target_channel == 'L':
            sweep_stereo[:len(sweep), 0] = sweep
        else:
            sweep_stereo[:len(sweep), 1] = sweep
        
        import time
        # Dynamically adopt the output device's native sample rate if it differs
        try:
            out_info = sd.query_devices(output_device_idx)
            native_sr = int(out_info['default_samplerate'])
            if native_sr != self.sample_rate:
                self.sample_rate = native_sr
                sweep, _ = self.generate_sweep(duration, f_start, f_end)
                inv_sweep = self.get_inverse_filter(sweep, duration, f_start, f_end)
                padding_samples = int(0.5 * self.sample_rate)
                sweep_stereo = np.zeros((len(sweep) + padding_samples, 2))
                if target_channel == 'L':
                    sweep_stereo[:len(sweep), 0] = sweep
                else:
                    sweep_stereo[:len(sweep), 1] = sweep
        except Exception:
            pass

        # 2. CoreAudio full-duplex I/O
        try:
            recording = sd.playrec(sweep_stereo, 
                                   samplerate=self.sample_rate, 
                                   channels=1, 
                                   device=(input_device_idx, output_device_idx),
                                   blocking=False)
        except sd.PortAudioError as e:
            # Fallback for some macOS interfaces that strictly require matching input channels
            if "9986" in str(e) or "9998" in str(e) or "Invalid number of channels" in str(e) or "Internal PortAudio error" in str(e):
                in_info = sd.query_devices(input_device_idx)
                in_chans = in_info['max_input_channels']
                recording = sd.playrec(sweep_stereo, 
                                       samplerate=self.sample_rate, 
                                       channels=in_chans, # Use exact max input channels
                                       device=(input_device_idx, output_device_idx),
                                       blocking=False)
            else:
                raise e
                               
        start_t = time.time()
        timeout = duration + 5.0
        # Wait for the stream to finish or timeout
        while sd.get_stream() is not None and sd.get_stream().active:
            if progress_callback:
                progress_callback(time.time() - start_t)
            time.sleep(0.015) # 60fps UI update rate
            if time.time() - start_t > timeout:
                sd.stop()
                raise RuntimeError("Audio Engine Timeout: The audio interface did not respond. Check macOS Microphone permissions.")

        
        # Ensure it finishes gracefully
        sd.wait()
        
        rec_signal = recording[:, 0]
        peak_amp = np.max(np.abs(rec_signal))
        peak_dbfs = 20 * np.log10(peak_amp + 1e-12)
        if peak_dbfs < -60.0:
            raise RuntimeError(f"Measurement failed (Signal too quiet: {peak_dbfs:.1f} dBFS).\n\nThe microphone only recorded background noise. Ensure the IEM is playing, the volume is up, and the correct mic is selected.")
                               
        # 3. Deconvolution via FFT convolution to get Impulse Response (IR)
        ir = fftconvolve(rec_signal, inv_sweep, mode='same')
        
        # Electrical Loopback Check
        peak_index = np.argmax(np.abs(ir))
        # FIX: Since rec_signal is now padded to 1.5s but inv_sweep is 1.0s, 
        # mode='same' places the zero-latency peak at len(inv_sweep) // 2, not len(ir) // 2.
        latency_samples = peak_index - (len(inv_sweep) // 2)
        latency_ms = (latency_samples / self.sample_rate) * 1000.0
        
        if abs(latency_ms) < 0.1:
            raise RuntimeError("Electrical Loopback Detected! The signal has zero acoustic delay. Turn off 'Direct Monitoring' on your audio interface and ensure you selected the correct measurement microphone.")
            
        # Advanced Electrical Loopback Check (Flatness)
        # IEMs are never perfectly flat. If the IR is perfectly flat, it's a hardware loopback
        # that slipped past the latency check (e.g., Direct Monitor with USB buffer delay).
        temp_fft = np.fft.rfft(ir)
        temp_mag = 20 * np.log10(np.abs(temp_fft) + 1e-12)
        temp_freqs = np.fft.rfftfreq(len(ir), 1 / self.sample_rate)
        valid = (temp_freqs > 100) & (temp_freqs < 10000)
        if np.any(valid):
            mag_range = np.max(temp_mag[valid]) - np.min(temp_mag[valid])
            if mag_range < 3.0:
                raise RuntimeError(f"Electrical Loopback Detected! The frequency response is completely flat ({mag_range:.1f} dB variance). You are measuring the soundcard itself, not the microphone.\n\nTurn off 'Direct Monitoring' / 'Loopback' on your audio interface, and check your input selection.")
        
        # SNR / Crest Factor Check to prevent "ghost" curves from background noise
        rms_ir = np.sqrt(np.mean(ir**2))
        crest_factor = 20 * np.log10((np.max(np.abs(ir)) + 1e-12) / (rms_ir + 1e-12))
        if crest_factor < 25.0:
            raise RuntimeError(f"Measurement failed: No valid sweep detected in the recording (SNR too low, Crest Factor: {crest_factor:.1f} dB).\n\n"
                               "The microphone only picked up background noise. Ensure the IEM is playing sound and is properly seated in the coupler.")
        
        # 4. Compute Frequency Response via FFT
        # WISSENSCHAFTLICHES UPDATE: Time-Domain Windowing!
        # We must window the IR to exclude background noise (from the 1s record time)
        # and more importantly: to exclude Farina's harmonic distortion impulses
        # which sit at -95ms and earlier. This dramatically cleans up the Phase and Magnitude!
        N = len(ir)
        
        # FIX: The global 'np.where' onset detection was catching Farina's harmonic distortion 
        # impulses (-81ms before the peak) if distortion was > 5%, causing catastrophic 
        # comb-filtering by windowing both the distortion and the main impulse!
        
        peak_idx = np.argmax(np.abs(ir))
        peak_amp_ir = np.abs(ir[peak_idx])
        
        # PRO-AUDIO UPDATE: Localized Onset detection
        # We only search up to 2ms *before* the main peak. This guarantees we find the true 
        # acoustic onset of the main impulse, completely ignoring Farina distortion impulses!
        search_pre = int(0.002 * self.sample_rate)
        search_start = max(0, peak_idx - search_pre)
        
        threshold = 0.05 * peak_amp_ir
        local_search_area = np.abs(ir[search_start:peak_idx])
        above_thresh = np.where(local_search_area > threshold)[0]
        
        if len(above_thresh) > 0:
            onset_idx = search_start + above_thresh[0]
        else:
            onset_idx = peak_idx
            
        # Window: -5ms before onset to +100ms after onset
        # (100ms perfectly captures sub-bass down to 10Hz in IEMs without grabbing too much noise)
        win_pre = int(0.005 * self.sample_rate)
        win_post = int(0.10 * self.sample_rate)
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
        mag = 20 * np.log10(np.abs(fft_res) + 1e-12) + spl_offset_db
        phase = np.angle(fft_res)
        
        # 5. Apply Microphone Calibration if provided
        if mic_cal_freqs is not None and mic_cal_mags is not None and len(mic_cal_freqs) > 1:
            # Interpolate the calibration points to match our FFT frequency bins
            cal_interp = np.interp(freqs, mic_cal_freqs, mic_cal_mags)
            mag += cal_interp
        
        # === DEBUG DUMP: Save all intermediate DSP results for diagnosis ===
        try:
            import os, time as _t
            dump_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_dumps')
            os.makedirs(dump_dir, exist_ok=True)
            stamp = _t.strftime('%Y%m%d_%H%M%S')
            dump_path = os.path.join(dump_dir, f'measure_debug_{stamp}_{target_channel}.npz')
            np.savez_compressed(dump_path,
                rec_signal=rec_signal,
                ir_raw=ir,
                ir_windowed=ir_windowed,
                ir_shifted=ir_shifted,
                freqs=freqs,
                mag_raw=mag,
                peak_idx=peak_idx,
                onset_idx=onset_idx,
                w_start=w_start,
                w_end=w_end,
                latency_ms=latency_ms,
                crest_factor=crest_factor,
                peak_dbfs=peak_dbfs,
                spl_offset_db=spl_offset_db,
                sample_rate=self.sample_rate,
            )
            print(f"[DEBUG] Dump saved: {dump_path}")
        except Exception as _e:
            print(f"[DEBUG] Dump failed: {_e}")
        
        return freqs, mag, phase, ir

    @staticmethod
    def smooth_spectrum(freqs, mag, phase=None, points=500):
        if points == 0 or len(freqs) < points:
            return freqs, mag, phase
            
        from scipy.stats import binned_statistic
        valid = freqs > 10
        f = freqs[valid]
        
        if len(f) == 0:
            return freqs, mag, phase
            
        m = mag[valid]
        p = phase[valid] if phase is not None else None
        
        bins = np.logspace(np.log10(15), np.log10(22000), points)
        
        m_smooth, bin_edges, _ = binned_statistic(f, m, statistic='mean', bins=bins)
        f_log = np.sqrt(bin_edges[:-1] * bin_edges[1:])
        
        mask = ~np.isnan(m_smooth)
        if not np.any(mask):
            return freqs, mag, phase
            
        m_smooth = np.interp(f_log, f_log[mask], m_smooth[mask])
        
        p_smooth = None
        if p is not None:
            p_s, _, _ = binned_statistic(f, p, statistic='mean', bins=bins)
            p_smooth = np.interp(f_log, f_log[mask], p_s[mask])
            
        return f_log, m_smooth, p_smooth

    def extract_thd(self, ir, duration, f_start=20.0, f_end=20000.0, harmonics=[2, 3, 4]):
        """
        Extracts Total Harmonic Distortion (THD) from the impulse response using Farina's Log Sine Sweep method.
        The harmonic impulses appear before the main fundamental impulse.
        
        Args:
            ir (np.ndarray): The deconvolved impulse response.
            duration (float): The duration of the sine sweep in seconds.
            f_start (float): The start frequency of the sweep.
            f_end (float): The end frequency of the sweep.
            harmonics (list): List of harmonic orders to extract (e.g., [2, 3, 4]).
            
        Returns:
            tuple: (freqs, thd_percentage)
        """
        from scipy.fft import rfft, rfftfreq
        from scipy.signal.windows import hann
        
        peak_idx = np.argmax(np.abs(ir))
        N = len(ir)
        freqs = rfftfreq(N, 1 / self.sample_rate)
        
        # Window the fundamental to exclude harmonics
        fund_win_len = int(0.08 * self.sample_rate)
        fund_start = max(0, peak_idx - fund_win_len)
        fund_end = min(N, peak_idx + fund_win_len)
        
        fund_ir = np.zeros_like(ir)
        fund_ir[fund_start:fund_end] = ir[fund_start:fund_end] * hann(fund_end - fund_start)
        
        fund_fft = rfft(fund_ir)
        fund_mag = np.abs(fund_fft) + 1e-12
        
        harmonic_energy = np.zeros_like(fund_mag)
        win_len = int(0.05 * self.sample_rate)
        half_win = win_len // 2
        
        for n in harmonics:
            # Time shift for n-th harmonic
            delta_t = duration * np.log(n) / np.log(f_end / f_start)
            offset_samples = int(delta_t * self.sample_rate)
            h_idx_expected = peak_idx - offset_samples
            
            if h_idx_expected - half_win < 0:
                continue
                
            # Local search for the exact peak
            search_rad = int(0.01 * self.sample_rate)
            s_start = max(0, h_idx_expected - search_rad)
            s_end = min(N, h_idx_expected + search_rad)
            if s_start >= s_end:
                continue
                
            local_peak = np.argmax(np.abs(ir[s_start:s_end]))
            h_idx_actual = s_start + local_peak
            
            # Windowing the harmonic
            h_start = max(0, h_idx_actual - half_win)
            h_end = min(N, h_idx_actual + half_win)
            if h_start >= h_end:
                continue
                
            h_ir = np.zeros_like(ir)
            h_ir[h_start:h_end] = ir[h_start:h_end] * hann(h_end - h_start)
            
            h_fft = rfft(h_ir)
            h_mag = np.abs(h_fft)
            
            harmonic_energy += h_mag ** 2
            
        thd = np.sqrt(harmonic_energy) / fund_mag
        thd_percentage = thd * 100.0
        
        return freqs, thd_percentage

    def extract_hohd(self, ir, duration, f_start=20.0, f_end=20000.0):
        """Extract High-Order Harmonic Distortion for Rub & Buzz detection.
        
        Uses the Farina method to extract harmonics 10-20 from the impulse response.
        Returns HOHD in dB relative to the fundamental (peak detection per KLIPPEL method).
        
        Args:
            ir: Deconvolved impulse response.
            duration: Sweep duration in seconds.
            f_start: Sweep start frequency.
            f_end: Sweep end frequency.
            
        Returns:
            tuple: (freqs, hohd_db) — frequencies and HOHD in dB relative to fundamental.
        """
        from scipy.fft import rfft, rfftfreq
        from scipy.signal.windows import hann
        
        peak_idx = np.argmax(np.abs(ir))
        N = len(ir)
        freqs = rfftfreq(N, 1 / self.sample_rate)
        
        # Fundamental: same windowing as extract_thd
        fund_win_len = int(0.08 * self.sample_rate)
        fund_start = max(0, peak_idx - fund_win_len)
        fund_end = min(N, peak_idx + fund_win_len)
        fund_ir = np.zeros_like(ir)
        fund_ir[fund_start:fund_end] = ir[fund_start:fund_end] * hann(fund_end - fund_start)
        fund_mag = np.abs(rfft(fund_ir)) + 1e-12
        
        # Extract harmonics 10 through 20
        hohd_energy = np.zeros_like(fund_mag)
        win_len = int(0.03 * self.sample_rate)  # Shorter window for high-order harmonics
        half_win = win_len // 2
        
        for n in range(10, 21):
            delta_t = duration * np.log(n) / np.log(f_end / f_start)
            offset_samples = int(delta_t * self.sample_rate)
            h_idx = peak_idx - offset_samples
            
            if h_idx - half_win < 0 or h_idx + half_win >= N:
                continue
            
            # Local peak search
            search_rad = int(0.005 * self.sample_rate)
            s_start = max(0, h_idx - search_rad)
            s_end = min(N, h_idx + search_rad)
            local_peak = np.argmax(np.abs(ir[s_start:s_end]))
            h_idx_actual = s_start + local_peak
            
            h_start = max(0, h_idx_actual - half_win)
            h_end = min(N, h_idx_actual + half_win)
            if h_start >= h_end:
                continue
            
            h_ir = np.zeros_like(ir)
            h_ir[h_start:h_end] = ir[h_start:h_end] * hann(h_end - h_start)
            h_mag = np.abs(rfft(h_ir))
            
            # Use PEAK (not sum) per KLIPPEL — worst-case harmonic at each freq
            hohd_energy = np.maximum(hohd_energy, h_mag)
        
        # Convert to dB relative to fundamental
        hohd_db = 20 * np.log10(hohd_energy / fund_mag + 1e-12)
        
        return freqs, hohd_db

    def calculate_csd(self, ir, t_max=0.005, slices=50, window_len=0.002):
        """
        Calculates the Cumulative Spectral Decay (CSD) or Waterfall plot.
        
        Args:
            ir (np.ndarray): The impulse response.
            t_max (float): The total time to analyze after the peak (in seconds).
            slices (int): The number of time slices (waterfall steps).
            window_len (float): The length of the sliding FFT window (in seconds).
            
        Returns:
            tuple: (freqs, times, csd_mag)
                   freqs: 1D array of frequencies
                   times: 1D array of time slice offsets in ms
                   csd_mag: 2D array of magnitudes in dB (shape: [slices, len(freqs)])
        """
        from scipy.fft import rfft, rfftfreq
        from scipy.signal.windows import hann
        
        peak_idx = np.argmax(np.abs(ir))
        win_samples = int(window_len * self.sample_rate)
        if win_samples % 2 == 1:
            win_samples += 1
            
        window = hann(win_samples)
        t_max_samples = int(t_max * self.sample_rate)
        step_samples = max(1, t_max_samples // slices)
        
        n_fft = max(2048, 2 ** int(np.ceil(np.log2(win_samples))))
        freqs = rfftfreq(n_fft, 1 / self.sample_rate)
        
        csd_mag = np.zeros((slices, len(freqs)))
        times = np.zeros(slices)
        
        for i in range(slices):
            offset = i * step_samples
            start_idx = peak_idx + offset
            end_idx = start_idx + win_samples
            
            if end_idx > len(ir):
                slice_ir = np.zeros(win_samples)
                avail = len(ir) - start_idx
                if avail > 0:
                    slice_ir[:avail] = ir[start_idx:len(ir)]
            else:
                slice_ir = ir[start_idx:end_idx]
                
            windowed = slice_ir * window
            fft_res = rfft(windowed, n=n_fft)
            
            mag = 20 * np.log10(np.abs(fft_res) + 1e-12)
            csd_mag[i, :] = mag
            times[i] = (offset / self.sample_rate) * 1000.0
            
        return freqs, times, csd_mag
