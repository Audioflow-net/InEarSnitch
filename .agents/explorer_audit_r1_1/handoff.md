# Handoff Report — R1. Deep QA (Logic & Math Audit)

**Agent:** `explorer_audit_r1_1`  
**Date:** 2026-09-24  
**Project:** InEar Snitch  
**Working Directory:** `/Users/ben/Desktop/InEarSnitch/.agents/explorer_audit_r1_1`  
**Target File for Analysis:** `/Users/ben/Desktop/InEarSnitch/.agents/explorer_audit_r1_1/analysis.md`  

---

## 1. Observation

Direct code examination and static analysis revealed 24 concrete issues in backend calculation routines, worker threads, and numerical signal processing:

1. **`analysis.py` Line 141**:
   ```python
   # analysis.py:140-141
   if thd_data is not None:
       thd_freqs, thd_l, thd_r = thd_data
   ```
   Whereas `main.py` line 4272 packs 5 items:
   ```python
   thd_data = (thd_freqs, thd_l, thd_r, hohd_l, hohd_r)
   ```
   When `thd_data` is passed to `Analyzer.run_full_diagnostics()` (called from `analysis_ui.py:1415`), Python raises:
   `ValueError: too many values to unpack (expected 3)`.

2. **`eq_math.py` Lines 17–18**:
   ```python
   w0 = 2 * np.pi * freq / fs
   alpha = np.sin(w0) / (2 * q)
   ```
   If `q == 0` (or `fs == 0`), execution raises:
   `ZeroDivisionError: float division by zero`.

3. **`main.py` Lines 603–612**:
   ```python
   # In LiveSealWorker.callback()
   mag = np.abs(np.fft.rfft(sig_w)) / (N_sig / 2.0)
   mag_smooth = M @ mag
   ```
   `M` is precomputed with shape `(n_bins, 4097)` assuming `self.blocksize = 8192`. If the PortAudio backend supplies a chunk with `frames != 8192` (e.g. 512, 1024, or leftover buffer), `len(mag) != 4097`, raising:
   `ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0`.

4. **`audio_engine.py` Lines 595–598 and 685–688**:
   ```python
   if noise_floor is not None:
       n_chunk_len = h_end - h_start
       mid = len(noise_floor) // 2
       n_ir = np.zeros_like(ir)
       n_ir[h_start:h_end] = noise_floor[mid - n_chunk_len//2 : mid - n_chunk_len//2 + n_chunk_len] * tukey(n_chunk_len, alpha=0.5)
   ```
   When `len(noise_floor) < n_chunk_len`, `mid - n_chunk_len//2 < 0`. Negative start indexing wraps around in Python slicing, creating a slice shorter than `n_chunk_len`. Multiplication with `tukey(n_chunk_len)` raises:
   `ValueError: operands could not be broadcast together with shapes`.

5. **`eq_math.py` Lines 54–80**:
   `self.filters` is mutated in-place by the real-time PortAudio thread (`f['_cached_zi'] = zf`) while the GUI thread calls `dsp_engine.set_filters()` and `AudioEngine.generate_sweep()` processes measurement sweeps, causing race conditions and state corruption.

6. **`audio_engine.py` Lines 148–150**:
   ```python
   expected_probe_peak = cal_rec_peak + 20 * np.log10(probe_amp / cal_sweep_amp + 1e-12)
   ```
   If `cal_sweep_amp == 0`, raises `ZeroDivisionError: float division by zero`.

7. **`audio_engine.py` Lines 86–87, 130, 224, 315**:
   `sd.query_devices(None)` returns a `DeviceList` (list of dictionaries). Accessing `sd.query_devices(None)['default_samplerate']` raises:
   `TypeError: list indices must be integers or slices, not str`.

8. **`audio_engine.py` Lines 464–468**:
   Interpolation `np.interp(np.log10(safe_freqs), np.log10(safe_cal_f), mic_cal_mags)` checks `len(mic_cal_freqs) > 1` but fails to check whether `len(mic_cal_mags) == len(mic_cal_freqs)`. If lengths differ, raises `ValueError: fp and xp are not of the same length`.

9. **`main.py` Lines 3795–3797**:
   `self.live_worker.terminate()` is called on timeout, forcefully aborting the thread while holding PortAudio internal stream mutexes.

10. **`main.py` (MainWindow lifecycle)**:
    No `closeEvent` handler is implemented. Closing the window while `LiveSealWorker`, `MeasurementWorker`, or `StressWorker` is running destroys parent QObjects and aborts with `QThread: Destroyed while thread is still running` (SIGABRT).

---

## 2. Logic Chain

1. **Step 1 (Tracing the Diagnostics Pipeline)**:
   - In `main.py:4272`, `thd_data` is constructed as `(thd_freqs, thd_l, thd_r, hohd_l, hohd_r)` (5 elements).
   - In `analysis_ui.py:1415`, `Analyzer.run_full_diagnostics` is called with `thd_data`.
   - In `analysis.py:141`, `thd_freqs, thd_l, thd_r = thd_data` attempts to unpack 5 elements into 3 variables.
   - **Inference**: Any measurement run with >= 3 sweeps will crash in `analysis.py:141` when rendering diagnostics.

2. **Step 2 (Tracing Real-Time Audio Callback Stability)**:
   - In `main.py:519`, `self.blocksize = 8192`. In lines 550–560, matrix `M` is allocated with shape `(n_bins, 4097)`.
   - In `main.py:572`, `callback(indata, outdata, frames, time, status)` receives `frames` from the host audio driver.
   - Host audio drivers (CoreAudio, WASAPI) are not required to provide exact powers of two or fixed block sizes on every callback cycle.
   - In lines 609–612, `N_sig = len(indata[:, 0]) = frames`. `mag = np.abs(np.fft.rfft(sig_w)) / (N_sig / 2.0)` produces length `frames // 2 + 1`.
   - `M @ mag` performs matrix multiplication between `(n_bins, 4097)` and `(frames // 2 + 1,)`.
   - **Inference**: Any deviation from `frames == 8192` causes an unhandled `ValueError` in the audio thread, terminating live RTA immediately.

3. **Step 3 (Tracing Filter State Concurrency)**:
   - `dsp_engine` is a global singleton instantiated at `eq_math.py:117`.
   - Its `process()` method iterates over `self.filters` and mutates `f['_cached_zi'] = zf` and `f['_cached_b'] = b`.
   - It is called concurrently by the PortAudio thread (`LiveSealWorker`), the sweep generator (`MeasurementWorker`), and the UI thread (`analysis_ui.py:update_dsp`).
   - **Inference**: Without a lock, simultaneous execution corrupts filter internal states across concurrent audio streams and risks iteration mutation crashes.

4. **Step 4 (Tracing Thread Lifecycle Termination)**:
   - When RTA is toggled off, `main.py:3796` calls `self.live_worker.terminate()`.
   - Termination during active PortAudio stream execution leaves PortAudio C library locks acquired.
   - Closing the GUI window without stopping workers triggers Qt's runtime assertion against deleting running `QThread` instances.
   - **Inference**: These thread handling patterns cause unpredictable deadlocks and SIGABRT crashes on exit.

---

## 3. Caveats

- **Scope boundary**: This audit is strictly read-only and analytical, focused on mathematical correctness, edge cases, thread safety, and exception handling in `audio_engine.py`, `eq_math.py`, and related backend workers. No source code modifications were made.
- **Hardware-dependent timings**: The PortAudio frame size mismatch (`Issue 4.1`) manifests primarily on devices/configurations where the audio driver uses variable buffer sizing or aggregate devices; on fixed 8192-frame hardware setups it may remain dormant until buffer underruns occur.

---

## 4. Conclusion

The application backend contains **1 Critical defect**, **10 High-severity defects**, **10 Medium-severity defects**, and **3 Low-severity defects**. 

The most urgent issues requiring remediation prior to release are:
1. **Critical:** Fix `analysis.py:141` tuple unpack to support 5-element `thd_data`.
2. **High:** Protect `eq_math.py:18` against `q <= 0`.
3. **High:** Implement FIFO buffering in `LiveSealWorker.callback()` to ensure `frames == 8192` for matrix multiplication `M @ mag`.
4. **High:** Fix slice bounds in `audio_engine.py:598` and `688` to avoid broadcast crashes during noise floor windowing.
5. **High:** Replace `live_worker.terminate()` with cooperative cancellation, and add `MainWindow.closeEvent` to ensure clean shutdown.

All 24 issues are documented with exact lines and failure mechanisms in `/Users/ben/Desktop/InEarSnitch/.agents/explorer_audit_r1_1/analysis.md`.

---

## 5. Verification Method

To independently verify the observations:

1. **Verify `thd_data` Unpack Crash:**
   ```bash
   python3 -c "
   thd_data = (None, None, None, None, None)
   try:
       thd_freqs, thd_l, thd_r = thd_data
   except ValueError as e:
       print('Verified unpack crash:', e)
   "
   ```
2. **Verify PortAudio Matrix Mismatch (`M @ mag`):**
   ```bash
   python3 -c "
   import numpy as np
   M = np.zeros((100, 4097))
   # Callback with frames=1024
   sig = np.zeros(1024)
   mag = np.abs(np.fft.rfft(sig))
   try:
       res = M @ mag
   except ValueError as e:
       print('Verified matmul mismatch crash:', e)
   "
   ```
3. **Verify Q=0 ZeroDivisionError in Biquad Calculation:**
   ```bash
   python3 -c "
   from eq_math import dsp_engine
   try:
       dsp_engine._get_biquad('peq', 1000, 3.0, 0.0, 48000)
   except ZeroDivisionError as e:
       print('Verified Q=0 crash:', e)
   "
   ```
4. **Verify Negative Slice Broadcast Crash in THD Noise Floor:**
   ```bash
   python3 -c "
   import numpy as np
   from scipy.signal.windows import tukey
   noise_floor = np.zeros(500)
   n_chunk_len = 2400
   mid = len(noise_floor) // 2
   start = mid - n_chunk_len // 2  # -950
   end = start + n_chunk_len       # 1450
   try:
       sliced = noise_floor[start:end] * tukey(n_chunk_len, alpha=0.5)
   except ValueError as e:
       print('Verified broadcast shape crash:', e)
   "
   ```
5. **Inspect Audit Report:**
   View `/Users/ben/Desktop/InEarSnitch/.agents/explorer_audit_r1_1/analysis.md`.
