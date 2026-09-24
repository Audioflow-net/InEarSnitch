# Deep QA Audit (Logic & Math) — InEar Snitch Backend & Workers

**Auditor:** `explorer_audit_r1_1`  
**Mission:** R1. Deep QA (Logic & Math) — Backend threads, math, and workers (`audio_engine.py`, `eq_math.py`, `main.py` workers, `analysis.py`, `database.py`)  
**Date:** 2026-09-24  
**Project Root:** `/Users/ben/Desktop/InEarSnitch`  

---

## Executive Summary

A comprehensive line-by-line audit of `audio_engine.py`, `eq_math.py`, and their interacting worker threads and analysis modules was conducted. 

A total of **24 distinct issues** were identified across five core categories:
1. **Division by Zero & Log Domain Exceptions (6 issues)**: Unprotected division by `q`, `fs`, `cal_sweep_amp`, `slices`, `duration`, and `f_end/f_start`.
2. **NoneType Dereferences & Unhandled None/Length Mismatches (5 issues)**: None device IDs causing list indexing crashes, missing mic calibration length checks, and tuple unpacking mismatches.
3. **Thread Safety, Worker Crashes & GUI Freezes (6 issues)**: Unsynchronized global DSP state accessed concurrently by real-time audio threads and UI, `live_worker.terminate()` killing PortAudio locks, PortAudio callback emitting Qt signals, and missing `closeEvent` terminating active QThreads abruptly.
4. **Buffer Shape & Dimension Mismatches (4 issues)**: Mismatched PortAudio chunk size vs. fixed 8192 log-binning matrix `M @ mag`, noise-floor negative slicing in THD/HOHD deconvolution.
5. **Numerical Edge Cases & NaN/Inf Propagation (3 issues)**: Empty array reduction operations (`np.max([])`, `np.argmax([])`), NaN propagation through SNR/crest calculations, and unclipped NaNs in DSP filtering.

---

## Detailed Findings

### Category 1: Division by Zero & Mathematical Domain Errors

#### Issue 1.1: Division by Zero on Q Factor in Biquad Filter Calculation
- **File:** `/Users/ben/Desktop/InEarSnitch/eq_math.py`
- **Lines:** 17–18
- **Code:**
```python
w0 = 2 * np.pi * freq / fs
alpha = np.sin(w0) / (2 * q)
```
- **Severity:** High
- **Failure Mechanism:** If `q == 0` (e.g., from an imported EQ preset, direct dial input, or reset parameter), `2 * q` evaluates to `0`. Python raises an unhandled `ZeroDivisionError: float division by zero`, crashing the audio processing thread or EQ response plotting immediately. Additionally, if `fs == 0`, `w0` computation triggers `ZeroDivisionError`.
- **Recommended Fix:** Clamp `q` to a strictly positive minimum (e.g., `q = max(float(q), 0.01)`) and ensure `fs = max(int(fs), 1)`.

---

#### Issue 1.2: Division by Zero in Calibration Sweep Ratio Prediction
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 148–150
- **Code:**
```python
if cal_rec_peak is not None and cal_sweep_amp is not None:
    # Expected probe peak = cal peak + 20*log10(probe_amp / cal_sweep_amp + 1e-12)
    expected_probe_peak = cal_rec_peak + 20 * np.log10(probe_amp / cal_sweep_amp + 1e-12)
```
- **Severity:** High
- **Failure Mechanism:** If `cal_sweep_amp` was saved as `0.0` or initialized to `0` (e.g., failed calibration saved to QSettings), `probe_amp / cal_sweep_amp` raises `ZeroDivisionError: float division by zero`. Preflight check crashes instead of returning a graceful warning.
- **Recommended Fix:** Check `if cal_rec_peak is not None and cal_sweep_amp and cal_sweep_amp > 1e-5:` before computing the ratio.

---

#### Issue 1.3: Division by Zero in Noise Floor Spectrum Normalization
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 195–196
- **Code:**
```python
freqs = np.fft.rfftfreq(len(recording), 1.0 / sr)
magnitude_db = 20 * np.log10(np.abs(spectrum) / len(recording) + 1e-12)
```
- **Severity:** Medium
- **Failure Mechanism:** If `duration <= 0` or stream returns an empty buffer (`len(recording) == 0`), `len(recording)` evaluates to zero. Division by `len(recording)` raises `ZeroDivisionError: division by zero` in Python or a `RuntimeWarning: divide by zero encountered in divide`.
- **Recommended Fix:** Verify `if len(recording) == 0:` and return early with safe fallback arrays.

---

#### Issue 1.4: Division by Zero in THD Harmonic Frequency Ratio
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Line:** 565
- **Code:**
```python
delta_t = duration * np.log(n) / np.log(f_end / f_start)
```
- **Severity:** Medium
- **Failure Mechanism:** If `f_end == f_start` (e.g., user configures a single-frequency sweep or test tone), `f_end / f_start == 1.0`. `np.log(1.0)` is `0.0`. Division by zero raises `ZeroDivisionError: float division by zero`. Furthermore, if `f_start <= 0` or `f_end <= 0`, `np.log` produces `NaN`/`RuntimeWarning`.
- **Recommended Fix:** Validate `if f_start <= 0 or f_end <= f_start:` and raise a clear ValueError or return empty arrays.

---

#### Issue 1.5: Integer Division by Zero & Overflow in CSD Slices & Hann Window
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 729–738
- **Code:**
```python
win_samples = int(window_len * self.sample_rate)
...
t_max_samples = int(t_max * self.sample_rate)
step_samples = max(1, t_max_samples // slices)

n_fft = max(2048, 2 ** int(np.ceil(np.log2(win_samples))))
freqs = rfftfreq(n_fft, 1 / self.sample_rate)
```
- **Severity:** Medium
- **Failure Mechanism:** 
  1. If `slices <= 0`, `t_max_samples // slices` raises `ZeroDivisionError: integer division or modulo by zero`.
  2. If `window_len <= 0`, `win_samples = 0`. `np.log2(0)` evaluates to `-inf`. `int(np.ceil(-inf))` raises `OverflowError: cannot convert float infinity to integer`.
  3. If `self.sample_rate <= 0`, `1 / self.sample_rate` raises `ZeroDivisionError`.
- **Recommended Fix:** Validate parameters at entry: `assert slices > 0`, `assert window_len > 0`, and `assert self.sample_rate > 0`.

---

#### Issue 1.6: Division by Zero and Non-Monotonic Interpolation in Auto-Calibration Routine
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 2550, 2558
- **Code:**
```python
optimal_amp = float(np.interp(target_peak, peaks, amps))
...
stress_peak = actual_peak + 20 * np.log10(stress_amp / optimal_amp + 1e-12)
```
- **Severity:** Medium
- **Failure Mechanism:**
  1. `np.interp(target_peak, peaks, amps)` assumes `peaks` is monotonically increasing. If the room has background noise, AGC, or acoustic anomalies where louder tones produce lower recorded peaks, `peaks` is not monotonic, causing `np.interp` to return corrupt amplitude values.
  2. If `optimal_amp == 0`, `stress_amp / optimal_amp` raises `ZeroDivisionError`.
- **Recommended Fix:** Sort `peaks` and `amps` strictly, ensure monotonicity, and guard `optimal_amp = max(optimal_amp, 0.001)`.

---

### Category 2: NoneType Dereferences & Unhandled None / Shape Mismatches

#### Issue 2.1: CRITICAL Crash: `thd_data` 5-Tuple vs 3-Variable Unpacking Mismatch in Diagnostics
- **File:** `/Users/ben/Desktop/InEarSnitch/analysis.py` (interfacing with `main.py` line 4272 and `analysis_ui.py` line 1415)
- **Line:** 141
- **Code:**
```python
# In analysis.py:
if thd_data is not None:
    thd_freqs, thd_l, thd_r = thd_data
```
Contrasted with `main.py` line 4272:
```python
if thd_freqs is not None:
    thd_data = (thd_freqs, thd_l, thd_r, hohd_l, hohd_r)
```
And `analysis_ui.py` lines 1480–1483:
```python
if thd_data is not None:
    if len(thd_data) == 5:
        thd_freqs, orig_thd_l, orig_thd_r, hohd_l, hohd_r = thd_data
    else:
        thd_freqs, orig_thd_l, orig_thd_r = thd_data
```
- **Severity:** Critical
- **Failure Mechanism:** In `main.py`, `thd_data` is stored as a 5-element tuple containing HOHD data. While `analysis_ui.py` was patched to check `if len(thd_data) == 5:`, `analysis.py` line 141 was NOT updated and still unpacks `thd_data` into exactly 3 variables: `thd_freqs, thd_l, thd_r = thd_data`. When the user runs measurements with sweeps >= 3x (enabling diagnostics), `Analyzer.run_full_diagnostics()` is called and immediately raises:
`ValueError: too many values to unpack (expected 3)`.
This uncaught exception on the GUI thread aborts analysis rendering completely.
- **Recommended Fix:** In `analysis.py`, support both 3 and 5 elements:
```python
if thd_data is not None:
    if len(thd_data) == 5:
        thd_freqs, thd_l, thd_r, _, _ = thd_data
    else:
        thd_freqs, thd_l, thd_r = thd_data
```

---

#### Issue 2.2: NoneType TypeError in `sd.query_devices(None)`
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 86–87, 130, 224–225, 315
- **Code:**
```python
out_info = sd.query_devices(output_device_idx)
native_sr = int(out_info['default_samplerate'])
...
in_chans = sd.query_devices(input_device_idx)['max_input_channels']
```
- **Severity:** High
- **Failure Mechanism:** In `sounddevice`, when the device argument is `None` (e.g., if user has not yet selected audio devices in settings), `sd.query_devices(None)` returns a `DeviceList` (a Python list of all devices in the system), NOT a dictionary. Slicing with string keys (`out_info['default_samplerate']` or `['max_input_channels']`) raises `TypeError: list indices must be integers or slices, not str`.
- **Recommended Fix:** Validate `if input_device_idx is not None and isinstance(input_device_idx, int):` before querying.

---

#### Issue 2.3: Unchecked Array Length Mismatch in Microphone Calibration Interpolation
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 464–468
- **Code:**
```python
if mic_cal_freqs is not None and mic_cal_mags is not None and len(mic_cal_freqs) > 1:
    # Interpolate the calibration points in log-space to match audio physics
    safe_freqs = np.clip(freqs, 1e-6, None)
    safe_cal_freqs = np.clip(mic_cal_freqs, 1e-6, None)
    cal_interp = np.interp(np.log10(safe_freqs), np.log10(safe_cal_freqs), mic_cal_mags)
    mag += cal_interp
```
- **Severity:** High
- **Failure Mechanism:** The code checks `len(mic_cal_freqs) > 1`, but fails to check whether `len(mic_cal_mags) == len(mic_cal_freqs)`. If a corrupted calibration file is parsed or lists differ in size, `np.interp` raises `ValueError: fp and xp are not of the same length`, terminating the measurement worker.
- **Recommended Fix:** Update condition to: `if mic_cal_freqs is not None and mic_cal_mags is not None and len(mic_cal_freqs) > 1 and len(mic_cal_freqs) == len(mic_cal_mags):`.

---

#### Issue 2.4: NoneType Crash in `_on_stress_done` Diagnostics Filtering
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 2777–2781
- **Code:**
```python
if hasattr(self.page_ana, '_last_report'):
    self.page_ana._last_report = [r for r in self.page_ana._last_report if r['title'] != 'Stress Test (Rub & Buzz)']
    self.page_ana._last_report.insert(0, report_item)
else:
    self.page_ana._last_report = [report_item]
```
- **Severity:** High
- **Failure Mechanism:** `hasattr(self.page_ana, '_last_report')` returns `True` even if `self.page_ana._last_report` is `None`. Iterating `[r for r in self.page_ana._last_report ...]` raises `TypeError: 'NoneType' object is not iterable`, crashing the stress test completion callback.
- **Recommended Fix:** Change check to: `if getattr(self.page_ana, '_last_report', None) is not None:`.

---

#### Issue 2.5: Uncaught `ValueError` on Corrupt Database BLOBs in Reference Loader
- **File:** `/Users/ben/Desktop/InEarSnitch/database.py`
- **Lines:** 187–189
- **Code:**
```python
freqs = np.frombuffer(row[0], dtype=np.float64) if row[0] else None
mag_l = np.frombuffer(row[1], dtype=np.float64) if row[1] else None
mag_r = np.frombuffer(row[2], dtype=np.float64) if row[2] else None
```
- **Severity:** Medium
- **Failure Mechanism:** Unlike lines 273 and 288 in `database.py` which wrap `frombuffer` in `try...except`, `load_reference_measurement` does not. If a blob byte length is not a multiple of 8 (e.g. truncated write, 32-bit float, or corrupt byte), `np.frombuffer` raises `ValueError: buffer size must be a multiple of element size`.
- **Recommended Fix:** Wrap `frombuffer` calls in `try...except Exception:` block and return `None` on failure.

---

### Category 3: Thread Safety, Worker Crashes & GUI Freezes

#### Issue 3.1: Thread Safety / Race Condition in Global `dsp_engine` In-Place Cache Mutation
- **File:** `/Users/ben/Desktop/InEarSnitch/eq_math.py`
- **Lines:** 54–80, 117
- **Code:**
```python
# eq_math.py
for f in self.filters:
    ...
    if (f.get('_cached_fs') != fs or ...):
        b, a = self._get_biquad(...)
        f['_cached_b'] = b
        f['_cached_a'] = a
        ...
        f['_cached_zi'] = None
    if f.get('_cached_zi') is None:
        f['_cached_zi'] = signal.lfilter_zi(f['_cached_b'], f['_cached_a']) * y[0]
        
    y, zf = signal.lfilter(f['_cached_b'], f['_cached_a'], y, zi=f['_cached_zi'])
    f['_cached_zi'] = zf
```
- **Severity:** High
- **Failure Mechanism:** `dsp_engine` is a global singleton instance. Its `process()` method is called continuously inside `LiveSealWorker.callback()` from the high-priority real-time audio thread, while `dsp_engine.set_filters()` and UI EQ parameter updates mutate `self.filters` from the main GUI thread. Additionally, `AudioEngine.generate_sweep()` calls `dsp_engine.process()` on measurement sweep arrays from `MeasurementWorker` or `StressWorker` threads.
  1. Modifying `self.filters` while `for f in self.filters:` is iterating can raise `RuntimeError: dictionary changed size during iteration` or `list changed size during iteration`.
  2. Simultaneous calls to `process()` from `LiveSealWorker` and `generate_sweep()` clobber each other's `_cached_zi` state (mixing state from 8192-sample noise chunks and 96000-sample sweeps), causing severe audio glitching, popping, or filter instability.
- **Recommended Fix:** Introduce a `threading.Lock` within `DSPEngine` or deep-copy filter parameters before iteration, maintaining separate filter state instances per stream.

---

#### Issue 3.2: Audio Thread Deadlock & PortAudio Lock Corruption via `live_worker.terminate()`
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 3795–3797
- **Code:**
```python
if hasattr(self, 'live_worker'):
    self.live_worker.stop()
    if not self.live_worker.wait(2000):  # 2s timeout
        self.live_worker.terminate()
        self.live_worker.wait(1000)
```
- **Severity:** High
- **Failure Mechanism:** In Qt, calling `QThread.terminate()` forcefully terminates a thread at an arbitrary instruction. If the thread is terminated while executing inside PortAudio C library routines (e.g. `sd.sleep(100)`, stream closing, or OS audio buffer release), PortAudio internal mutex locks remain permanently acquired or memory structures corrupted. Subsequent attempts to open an audio stream hang indefinitely or crash with `SIGSEGV`.
- **Recommended Fix:** Never call `.terminate()`. Ensure the audio stream in `LiveSealWorker` checks `self.running` and closes cleanly via `sd.CallbackStop` or `stream.abort()`.

---

#### Issue 3.3: Missing `closeEvent` on `MainWindow` Causing Fatal Thread Abort
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 739–750 (and class MainWindow throughout)
- **Code:**
No `closeEvent` method is defined on `MainWindow`.
- **Severity:** High
- **Failure Mechanism:** If the user closes the application window while `LiveSealWorker`, `MeasurementWorker`, or `StressWorker` is actively running, PySide6 destroys the `MainWindow` and its child QObjects. When a running `QThread`'s C++ object is deleted while still executing, Qt calls `qFatal` resulting in:
`Fatal Python error: Aborted` / `QThread: Destroyed while thread is still running` (SIGABRT).
- **Recommended Fix:** Implement `closeEvent(self, event)` on `MainWindow` to gracefully stop and wait for `live_worker`, `worker`, and `_stress_worker` before accepting the close event.

---

#### Issue 3.4: Duplicate Signal Emission on Error in `MeasurementWorker`
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 700–701
- **Code:**
```python
except Exception as e:
    import traceback
    traceback.print_exc()
    self.error.emit(str(e))  # Prints to stderr, which LogStream catches!
    self.error.emit(str(e))
```
- **Severity:** Low
- **Failure Mechanism:** `self.error.emit(str(e))` is copy-pasted twice in the exception handler. If a measurement fails, the connected slot (`on_measurement_error`) is invoked twice, resulting in duplicate error dialog popups or duplicate status resets.
- **Recommended Fix:** Remove the duplicate line 701.

---

#### Issue 3.5: Preflight Check Silently Conceals Fatal Device Errors
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 132–133
- **Code:**
```python
except Exception as e:
    return True, -999.0, f"Pre-flight skipped: {e}"
```
- **Severity:** Medium
- **Failure Mechanism:** If the audio interface fails to open during preflight check (e.g. invalid sample rate, device disconnected, permission denied), the exception is caught and returns `True` for `passed`. The calling code in `main.py:4050` checks `if not passed:`, so it assumes preflight succeeded and proceeds to launch the full measurement sweep, which immediately crashes or hangs.
- **Recommended Fix:** Return `False, -999.0, f"Pre-flight failed: {e}"` on actual device initialization errors.

---

#### Issue 3.6: Blocking GUI Thread Execution in Auto-Calibration Routine
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 2448–2520
- **Code:**
```python
for amp in steps:
    ...
    with sd.Stream(...) as stream:
        event.wait(timeout=1.0)
    ...
    QApplication.processEvents()
```
- **Severity:** Medium
- **Failure Mechanism:** The auto-calibration loop runs up to 10 sequential 1-second audio streams directly inside the main GUI thread, relying on `QApplication.processEvents()` between steps. During each 1.0s stream wait, the GUI thread is completely blocked in `event.wait(timeout=1.0)`, making the window unresponsive (spinning beachball on macOS) and vulnerable to OS app-not-responding (ANR) warnings.
- **Recommended Fix:** Offload the auto-calibration sequence to a dedicated `QThread` worker.

---

### Category 4: Buffer Shape & Dimension Mismatches

#### Issue 4.1: CRITICAL Crash: PortAudio Callback Frame Mismatch in Matrix Multiplication
- **File:** `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines:** 603–612
- **Code:**
```python
sig = indata[:, 0].copy()
N_sig = len(sig)
sig_w = sig * window[:N_sig] if N_sig <= len(window) else sig * np.hanning(N_sig)

mag = np.abs(np.fft.rfft(sig_w)) / (N_sig / 2.0)

# Fast fractional octave log-binning
mag_smooth = M @ mag
```
- **Severity:** High
- **Failure Mechanism:** Matrix `M` is precomputed with shape `(n_bins, 4097)` based strictly on `self.blocksize = 8192` (`8192 // 2 + 1 = 4097`). PortAudio backends (WASAPI on Windows, CoreAudio on macOS, or Bluetooth/USB aggregate devices) do not guarantee that every audio callback invocation contains exactly `frames == self.blocksize` (e.g., driver buffer underruns, smaller adapter buffer size like 512 or 1024 frames, or stream flush). When `frames != 8192`, `len(mag) != 4097`. The matrix multiplication `M @ mag` immediately raises:
`ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0`.
This unhandled error inside the audio callback causes `LiveSealWorker` to abort and crash live RTA.
- **Recommended Fix:** Buffer incoming frames into an internal FIFO accumulator of exact size 8192 before performing FFT and matrix multiplication, or recompute/interpolate `mag` to match `M.shape[1]`.

---

#### Issue 4.2: Negative Slice Wrapping & Broadcast Error in THD Noise Floor Windowing
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 595–598
- **Code:**
```python
if noise_floor is not None:
    n_chunk_len = h_end - h_start
    mid = len(noise_floor) // 2
    n_ir = np.zeros_like(ir)
    n_ir[h_start:h_end] = noise_floor[mid - n_chunk_len//2 : mid - n_chunk_len//2 + n_chunk_len] * tukey(n_chunk_len, alpha=0.5)
```
- **Severity:** High
- **Failure Mechanism:** If `len(noise_floor) < n_chunk_len` (e.g., if a short noise floor buffer was captured or loaded from state), `mid - n_chunk_len // 2` is negative. In Python array slicing, a negative index wraps around to the end of the array. The slice length `len(noise_floor[...])` will be smaller than `n_chunk_len`. Multiplying with `tukey(n_chunk_len, alpha=0.5)` raises:
`ValueError: operands could not be broadcast together with shapes (...) (n_chunk_len,)`.
If this occurs, `extract_thd` crashes during post-measurement processing.
- **Recommended Fix:** Explicitly check bounds: ensure `start = max(0, mid - n_chunk_len//2)` and pad `noise_floor` with zeros if `len(noise_floor) < n_chunk_len`.

---

#### Issue 4.3: Identical Negative Slice Wrapping & Broadcast Error in HOHD Extraction
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 685–688
- **Code:**
```python
if noise_floor is not None:
    n_chunk_len = h_end - h_start
    mid = len(noise_floor) // 2
    n_ir = np.zeros_like(ir)
    n_ir[h_start:h_end] = noise_floor[mid - n_chunk_len//2 : mid - n_chunk_len//2 + n_chunk_len] * tukey(n_chunk_len, alpha=0.5)
```
- **Severity:** High
- **Failure Mechanism:** Exact duplicate of Issue 4.2 in `extract_hohd`. When `len(noise_floor) < n_chunk_len`, negative slice indexing produces a shape mismatch and raises `ValueError`.
- **Recommended Fix:** Implement safe zero-padding and slice clamping.

---

#### Issue 4.4: Dynamic Sample Rate Switching Drops Amplitude Parameter
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 226–229
- **Code:**
```python
if native_sr != self.sample_rate:
    self.sample_rate = native_sr
    sweep, _ = self.generate_sweep(duration, f_start, f_end)
```
- **Severity:** Medium
- **Failure Mechanism:** In `AudioEngine.measure()`, when the output device native sample rate differs from default, `self.generate_sweep(duration, f_start, f_end)` is re-called, but `amplitude=amplitude` IS OMITTED. If the caller requested a specific amplitude (e.g., stress test at 0.25 amplitude), the sweep regenerates at the default calibrated level instead of the requested amplitude, invalidating stress test measurements.
- **Recommended Fix:** Pass `amplitude=amplitude` in line 228: `sweep, _ = self.generate_sweep(duration, f_start, f_end, amplitude=amplitude)`.

---

### Category 5: Numerical Edge Cases & NaN/Inf Propagation

#### Issue 5.1: `ValueError: zero-size array` on Empty Audio Buffer in `preflight_check` and `measure`
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 135, 342, 543, 633, 728
- **Code:**
```python
# Line 135:
peak_amp = np.max(np.abs(rec))
# Line 342:
peak_amp = np.max(np.abs(rec_signal))
# Line 543:
peak_idx = np.argmax(np.abs(ir))
```
- **Severity:** High
- **Failure Mechanism:** If the recording stream delivers 0 samples (due to device timeout or silence truncation `rec_signal_full[silence_samples:]` when total samples <= silence samples), `len(rec) == 0`. Calling `np.max()` or `np.argmax()` on an empty sequence raises:
`ValueError: zero-size array to reduction operation maximum which has no identity` or `ValueError: attempt to get argmax of an empty sequence`.
- **Recommended Fix:** Validate `if len(rec_signal) == 0:` before calling reduction functions and raise a descriptive `RuntimeError("Audio recording buffer is empty. Check device connections.")`.

---

#### Issue 5.2: Silent NaN Propagation in SNR and Crest Factor Checks
- **File:** `/Users/ben/Desktop/InEarSnitch/audio_engine.py`
- **Lines:** 392–394
- **Code:**
```python
rms_ir = np.sqrt(np.mean(ir**2))
crest_factor = 20 * np.log10((np.max(np.abs(ir)) + 1e-12) / (rms_ir + 1e-12))
if crest_factor < 25.0:
    raise RuntimeError(...)
```
- **Severity:** Medium
- **Failure Mechanism:** If `ir` contains `NaN` values (from driver glitches or unstable DSP filters), `np.mean(ir**2)` is `NaN`, and `crest_factor` becomes `NaN`. In Python, `NaN < 25.0` evaluates to `False`. The check is bypassed, and corrupted `NaN` arrays are processed through FFT and passed to UI, causing blank plots without warning.
- **Recommended Fix:** Check `if not np.all(np.isfinite(ir)) or np.isnan(crest_factor):` and raise a descriptive `RuntimeError("Measurement signal contains invalid numerical values (NaN/Inf).")`.

---

#### Issue 5.3: SciPy `lfilter_zi` Crash on Unstable Filter Poles
- **File:** `/Users/ben/Desktop/InEarSnitch/eq_math.py`
- **Lines:** 75–76
- **Code:**
```python
if f.get('_cached_zi') is None:
    f['_cached_zi'] = signal.lfilter_zi(f['_cached_b'], f['_cached_a']) * y[0]
```
- **Severity:** Medium
- **Failure Mechanism:** If filter parameters specify a center frequency at or above Nyquist (`freq >= fs / 2`) or zero frequency (`freq == 0`), the biquad poles lie on or outside the unit circle in the z-plane. `scipy.signal.lfilter_zi` strictly requires stability:
`ValueError: Compute of lfilter_zi failed: a[0] must not be 0 and system must be stable.`
Because line 76 has no `try...except`, this uncaught `ValueError` terminates the audio thread.
- **Recommended Fix:** Wrap `signal.lfilter_zi` in a `try...except ValueError:` block, falling back to zeros: `f['_cached_zi'] = np.zeros(max(len(f['_cached_b']), len(f['_cached_a'])) - 1)`.

---

## Summary Matrix of Audited Files & Issues

| ID | File | Line(s) | Type | Severity |
|---|---|---|---|---|
| 1.1 | `eq_math.py` | 17–18 | Division by zero (`q=0`, `fs=0`) | High |
| 1.2 | `audio_engine.py` | 148–150 | Division by zero (`cal_sweep_amp=0`) | High |
| 1.3 | `audio_engine.py` | 195–196 | Division by zero (`len(recording)=0`) | Medium |
| 1.4 | `audio_engine.py` | 565 | Division by zero (`f_end == f_start`) | Medium |
| 1.5 | `audio_engine.py` | 729–738 | Division by zero & Overflow (`slices=0`, `window_len=0`) | Medium |
| 1.6 | `main.py` | 2550, 2558 | Non-monotonic interpolation & Div by zero | Medium |
| 2.1 | `analysis.py` | 141 | Critical 5-tuple vs 3-variable unpack crash | **Critical** |
| 2.2 | `audio_engine.py` | 86–87, 130, 224, 315 | TypeError: list indexing on `sd.query_devices(None)` | High |
| 2.3 | `audio_engine.py` | 464–468 | Unchecked length mismatch in calibration interpolation | High |
| 2.4 | `main.py` | 2777–2781 | TypeError: iterating `NoneType` in `_last_report` | High |
| 2.5 | `database.py` | 187–189 | Uncaught `ValueError` on corrupt BLOB in `frombuffer` | Medium |
| 3.1 | `eq_math.py` | 54–80 | Race condition on global `dsp_engine` filter state | High |
| 3.2 | `main.py` | 3795–3797 | PortAudio deadlock via `live_worker.terminate()` | High |
| 3.3 | `main.py` | 739–750 | Missing `closeEvent` causes SIGABRT on window close | High |
| 3.4 | `main.py` | 700–701 | Duplicate error signal emission in MeasurementWorker | Low |
| 3.5 | `audio_engine.py` | 132–133 | Preflight returns `passed=True` on fatal stream error | Medium |
| 3.6 | `main.py` | 2448–2520 | Blocking GUI thread during auto-calibration loop | Medium |
| 4.1 | `main.py` | 603–612 | Matrix dimension mismatch `M @ mag` on variable frames | High |
| 4.2 | `audio_engine.py` | 595–598 | Negative slice index broadcast crash in THD noise floor | High |
| 4.3 | `audio_engine.py` | 685–688 | Negative slice index broadcast crash in HOHD noise floor | High |
| 4.4 | `audio_engine.py` | 226–229 | Sample rate switch drops `amplitude` parameter | Medium |
| 5.1 | `audio_engine.py` | 135, 342, 543 | `ValueError: zero-size array` on empty buffers | High |
| 5.2 | `audio_engine.py` | 392–394 | Silent NaN bypass in SNR / crest factor checks | Medium |
| 5.3 | `eq_math.py` | 75–76 | Uncaught `ValueError` in `lfilter_zi` on unstable poles | Medium |
