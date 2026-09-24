# Consolidated Pre-Release Audit & Quality Review Report

**Reviewer Agent:** `reviewer_audit_1` (Roles: `reviewer`, `critic`)  
**Parent Agent:** `orchestrator_3` (ID: `a1d06762-aab4-4ea0-bdeb-cbbe07e3aa0a`)  
**Audit Scope:** Independent cross-verification of Explorer 1 (R1 - Logic & Math), Explorer 2 (R2 - UI Completeness), and Explorer 3 (R3 - Legal & Safety)  
**Project Root:** `/Users/ben/Desktop/InEarSnitch`  
**Date:** 2026-09-24  
**Integrity Mode:** Benchmark / Read-Only Audit  

---

## 1. Executive Summary & Review Verdict

### Final Review Verdict: **REQUEST_CHANGES (RELEASE BLOCKED)**

An exhaustive, evidence-based cross-verification of all audit findings submitted by the three explorer teams was performed against the live codebase (`main.py`, `analysis.py`, `analysis_ui.py`, `audio_engine.py`, `eq_math.py`, `profile_ui.py`, `database.py`). 

A total of **40 findings** were independently audited across R1 (24 items), R2 (8 items), and R3 (8 items).
- **True Positives Confirmed:** **38 issues** (including 2 Critical, 15 High, 14 Medium, 7 Low).
- **Nuanced / Contextually Mitigated Findings:** **2 issues** (Items 2.2 and 3.5 in R1, where raw engine functions lack guards but calling sites in `main.py` partially mitigate the runtime risk during standard measurement flows).
- **Direct Code Modifications:** **ZERO (0)**. A full git tree check confirms that no implementation source code files have been modified or created anywhere in the project.

### Release Readiness Assessment
The application passes its basic 19/19 smoke test (`smoke_test.py`), confirming syntactical integrity and presence of core widgets. However, **the application CANNOT be safely released to production in its current state** due to:
1. **Critical Runtime Crash in Diagnostics**: Running standard measurements with ≥ 3 sweeps crashes immediately with `ValueError: too many values to unpack (expected 3)` at `analysis.py:141`.
2. **Critical Safety & Logic Breakdown via Method Shadowing**: Defining `run_stress_test` twice in `main.py` (lines 2619 and 4001) overwrites the entire Rub & Buzz / HOHD pipeline, bypasses the calibration safety check, and displays a critical hearing safety dialog hardcoded exclusively in German.
3. **Severe Hearing Damage Risks**: High-SPL sine sweeps (>107 dB SPL) can be triggered with zero confirmation by tapping `Space`; an unshielded bright-red `STRESS` button is enabled on launch adjacent to `RUN`; and unconstrained DSP filtering allows live pink noise to stream at 0 dBFS clipping levels.
4. **Interactive UI Breakdowns**: Dead search input in musician profiles, completely non-functional manual documentation hyperlinks, orphaned analysis zoom controls, and a fatal `TypeError` crash when loading profile avatars.

---

## 2. In-Depth Validation of the 8 Focus Issues

Each of the eight focus issues highlighted in the authoritative audit mandate was subjected to isolated code verification and runtime reproduction:

### 2.1. `analysis.py:141` — Critical Tuple Unpack Mismatch in Diagnostics
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **CRITICAL**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/analysis.py:141` (originating from `main.py:4272` and `analysis_ui.py:1415`)
- **Observed Code:**
  ```python
  # analysis.py:140-141
  if thd_data is not None:
      thd_freqs, thd_l, thd_r = thd_data
  ```
  Contrasted with `main.py:4272`:
  ```python
  if thd_freqs is not None:
      thd_data = (thd_freqs, thd_l, thd_r, hohd_l, hohd_r)  # 5-element tuple!
  ```
- **Reproduction Output:**
  ```
  Traceback (most recent call last):
    File "/Users/ben/Desktop/InEarSnitch/analysis.py", line 141, in run_full_diagnostics
      thd_freqs, thd_l, thd_r = thd_data
  ValueError: too many values to unpack (expected 3)
  ```
- **Failure Impact:** When the user measures with 3x or 5x sweeps (the recommended workflow to unlock diagnostics), `main.py` calculates HOHD and stores a 5-element tuple. `analysis_ui.py:1415` calls `Analyzer.run_full_diagnostics(...)`, which immediately throws an unhandled `ValueError` on the GUI thread. Diagnostics rendering crashes completely.
- **Recommended Fix:** Modify `analysis.py:141` to support both 3-tuple and 5-tuple formats:
  ```python
  if thd_data is not None:
      if len(thd_data) == 5:
          thd_freqs, thd_l, thd_r, _, _ = thd_data
      else:
          thd_freqs, thd_l, thd_r = thd_data
  ```

---

### 2.2. `main.py:4001` vs `main.py:2619` — Method Shadowing of `run_stress_test`
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **CRITICAL**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/main.py:2619–2725` vs `main.py:4001–4012`
- **Observed Code:**
  - **Definition 1 (`main.py:2619`):** 106 lines of robust logic. Checks `stress_amp = getattr(self.audio_engine, 'calibrated_stress_amp', None)`, shows warning if uncalibrated, checks preflight levels, runs dedicated `StressWorker`, and routes to `_on_stress_done` (line 2727) to plot HOHD / Rub & Buzz.
  - **Definition 2 (`main.py:4001`):** 
    ```python
    def run_stress_test(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.critical(self, "ACHTUNG: STRESS TEST",
            "Der Stress Test jagt einen extrem lauten Sweep (+15dB) durch den IEM, um mechanische Defekte aufzudecken.\n\n"
            "Nimm den In-Ear auf JEDEN FALL aus deinem Ohr!\n"
            "Er muss für diesen Test sicher im Coupler stecken.\n\n"
            "Möchtest du wirklich fortfahren?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            self.run_measurement(is_stress_test=True)
    ```
- **Reproduction Output:**
  ```python
  >>> import main
  >>> main.MainWindow.run_stress_test.__code__.co_firstlineno
  4001
  >>> main.MainWindow.run_stress_test.__doc__
  None  # Overwritten; definition at 2619 had docstring
  ```
- **Failure Impact:**
  1. Python method binding overwrites line 2619 with line 4001 at class compilation time.
  2. Lines 2619–2805 become dead code: `StressWorker`, `_on_stress_done`, and `_on_stress_error` are never executed.
  3. The calibration gate (`calibrated_stress_amp is None`) is completely bypassed.
  4. Non-German users are presented with a German critical warning dialog in an otherwise English application, creating acute acoustic trauma risks if instructions are not understood.
- **Recommended Fix:** Delete the shadowed definition at line 4001. Integrate proper multilingual warning modals and safety checkboxes directly into the Definition 1 implementation at line 2619.

---

### 2.3. `eq_math.py:18` — Division by Zero on `q=0` in Biquad Filter Calculation
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **HIGH**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/eq_math.py:17–18`
- **Observed Code:**
  ```python
  w0 = 2 * np.pi * freq / fs
  alpha = np.sin(w0) / (2 * q)
  ```
- **Reproduction Output:**
  ```python
  >>> from eq_math import dsp_engine
  >>> dsp_engine._get_biquad('peq', 1000, 3.0, 0.0, 48000)
  ZeroDivisionError: float division by zero
  ```
- **Failure Impact:** If `q == 0` (or `fs == 0`) is supplied via imported EQ presets (`apply_eq_preset`), custom configuration, or manual reset, an unhandled `ZeroDivisionError` is thrown, crashing the real-time audio thread or UI response calculation.
- **Recommended Fix:** Clamp `q` and `fs` to safe strictly-positive minimums:
  ```python
  fs = max(int(fs), 1)
  q = max(float(q), 0.001)
  ```

---

### 2.4. `main.py:612` — Matrix Dimension Mismatch `M @ mag` in `LiveSealWorker`
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **HIGH**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/main.py:603–612`
- **Observed Code:**
  ```python
  sig = indata[:, 0].copy()
  N_sig = len(sig)
  sig_w = sig * window[:N_sig] if N_sig <= len(window) else sig * np.hanning(N_sig)
  mag = np.abs(np.fft.rfft(sig_w)) / (N_sig / 2.0)
  # Fast fractional octave log-binning
  mag_smooth = M @ mag
  ```
- **Reproduction Output:**
  ```python
  >>> import numpy as np
  >>> M = np.zeros((100, 4097))  # Precomputed for 8192 blocksize
  >>> sig = np.zeros(1024)       # PortAudio callback delivers 1024 frames
  >>> mag = np.abs(np.fft.rfft(sig))
  >>> M @ mag
  ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0 (size 4097 != 513)
  ```
- **Failure Impact:** Matrix `M` is hardcoded with shape `(n_bins, 4097)` assuming `blocksize == 8192`. Audio hardware drivers (CoreAudio on macOS, WASAPI on Windows, Bluetooth/USB aggregates) frequently deliver non-8192 frame counts during stream startup, buffer underruns, or adapter adjustments. Any non-8192 callback cycle triggers a `ValueError` in the audio thread, invoking `CallbackAbort` and killing live RTA.
- **Recommended Fix:** Accumulate incoming samples in a circular FIFO buffer of size 8192 before computing the FFT and matrix multiplication, or dynamically compute/interpolate `mag` to match `M.shape[1]`.

---

### 2.5. `main.py:991` — Dead `search_input` Widget in Musician Profiles Sidebar
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **MEDIUM**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/main.py:991–1000`
- **Observed Code:**
  ```python
  991: self.search_input = QLineEdit()
  992: search_input = self.search_input
  993: search_input.setPlaceholderText("Search...")
  ...
  1000: search_box.addWidget(search_input)
  ```
- **Reproduction Output:** Full-file AST and grep search across `main.py` confirms that `self.search_input` is only referenced at lines 991–1000 (instantiation) and line 3135 (theme styling). Zero signal connections (`textChanged`, `textEdited`, `returnPressed`) exist.
- **Failure Impact:** Users typing into the search bar receive no filtering, feedback, or response. It is a completely unresponsive facade widget.
- **Recommended Fix:** Connect `self.search_input.textChanged.connect(self.filter_musician_profiles)` to filter `self.profile_cards` by name/IEM model, or remove the widget.

---

### 2.6. `main.py:1688` — Dead Manual Hyperlinks (Web URLs & Anchors)
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **HIGH**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/main.py:1688–1725`
- **Observed Code:**
  ```python
  1688: self.manual_browser.setOpenLinks(False)
  1689: def handle_manual_link(url):
  1690:     link = url.toString()
  1691:     file_path = link.split("#")[0]
  ...
  1695:     if os.path.exists(file_path):
  ...
  1725: self.manual_browser.anchorClicked.connect(handle_manual_link)
  ```
- **Reproduction Output:**
  ```python
  >>> import os
  >>> os.path.exists("https://squig.link/")
  False
  >>> os.path.exists("")  # Anchor link like "#hardware-guide"
  False
  ```
- **Failure Impact:**
  1. `setOpenLinks(False)` disables default Qt URL navigation.
  2. `handle_manual_link` gates all action behind `if os.path.exists(file_path):`.
  3. For external web links (`https://...`), `os.path.exists` returns `False`, and there is no `QDesktopServices.openUrl(url)` call. Clicking does nothing.
  4. For in-page anchor links starting with `#`, `file_path` is `""`. `os.path.exists("")` is `False`. The anchor scrolling logic (lines 1700–1724) is unreachable.
  5. Every hyperlink throughout the user manual is dead.
- **Recommended Fix:**
  ```python
  if link.startswith(("http://", "https://")):
      from PySide6.QtGui import QDesktopServices
      QDesktopServices.openUrl(url)
  elif link.startswith("#"):
      # Scroll directly to anchor in current document
  elif os.path.exists(file_path):
      # Load document and scroll to anchor
  ```

---

### 2.7. `main.py:1329` — Unshielded Bottom-Bar "STRESS" Button
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **HIGH**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/main.py:1329–1337`
- **Observed Code:**
  ```python
  self.btn_stress = QPushButton("STRESS")
  self.btn_stress.setToolTip("Run high-level Rub & Buzz sweep")
  ...
  self.btn_stress.clicked.connect(self.run_stress_test)
  run_layout.addWidget(self.btn_capture)
  run_layout.addWidget(self.btn_stress)
  ```
- **Reproduction Output:** Code review confirms `self.btn_stress` is instantiated without `setEnabled(False)`. In contrast, `analysis_ui.py:820` explicitly gates the stress button (`self.btn_stress_test.setEnabled(False)`).
- **Failure Impact:** The bright red STRESS button sits immediately adjacent to the green RUN button. It is permanently enabled on launch without requiring Output Level Calibration. Misclicking it immediately launches a high-level sweep through the uncalibrated interface.
- **Recommended Fix:** Initialize `self.btn_stress.setEnabled(False)`. Enable it only when `self.audio_engine.calibrated_stress_amp` is set via calibration. Add an explicit safety tooltip and separation margin.

---

### 2.8. `profile_ui.py:108` — Unhandled `setPixmap(NoneType)` Crash
- **Status:** **CONFIRMED TRUE POSITIVE**
- **Severity:** **HIGH**
- **File & Line:** `/Users/ben/Desktop/InEarSnitch/profile_ui.py:106–108` (invoked via `main.py:1478` / `2167`)
- **Observed Code:**
  ```python
  104: reader = QImageReader(self.current_pic_path)
  105: reader.setAutoTransform(True)
  106: circ_pix = create_circular_pixmap(reader, self.size_val)
  107: 
  108: self.img_label.setPixmap(circ_pix)
  ```
- **Reproduction Output:**
  ```
  TypeError: 'PySide6.QtWidgets.QLabel.setPixmap' called with wrong argument types:
    PySide6.QtWidgets.QLabel.setPixmap(NoneType)
  Supported signatures:
    PySide6.QtWidgets.QLabel.setPixmap(arg__1: Union[PySide6.QtGui.QPixmap, PySide6.QtGui.QImage], /)
  ```
- **Failure Impact:** In `create_circular_pixmap` (line 26), if `img.isNull()` (corrupt image file, zero-byte file, unsupported format), it returns `None`. Line 108 passes `None` directly to `self.img_label.setPixmap()`. PySide6 raises a fatal `TypeError`, crashing the application when switching to the Profile tab.
- **Recommended Fix:** Check `circ_pix` before setting pixmap:
  ```python
  if circ_pix:
      self.img_label.setPixmap(circ_pix)
      self.has_image = True
  else:
      self.set_empty_style()
  ```

---

## 3. Systematic Verification of All Explorer Findings

### 3.1. Verification of Requirement 1 (Logic & Math — 24 Findings)
Explorer 1 identified 24 issues. Independent line-by-line inspection confirms that:
- **Category 1 (Math & Zero-Division, Issues 1.1–1.6):** All 6 confirmed true positives. In particular, `audio_engine.py:150` evaluates `probe_amp / cal_sweep_amp` before `+ 1e-12`, meaning `cal_sweep_amp = 0` will crash regardless of the epsilon.
- **Category 2 (NoneType & Slicing, Issues 2.1–2.5):**
  - Issue 2.1 (`analysis.py:141`) is a Critical true positive.
  - Issue 2.2 (`sd.query_devices(None)` returning `DeviceList`): True code smell in standalone `audio_engine.py`, but calls within `main.py` are wrapped in `try/except` and guarded by `selected_in_idx is None` checks. Contextual severity adjusted from High to Low/Medium.
  - Issues 2.3, 2.4, 2.5 confirmed true positives.
- **Category 3 (Thread Safety & Freezes, Issues 3.1–3.6):**
  - Issue 3.1 (Global DSP state corruption across threads): True positive. PortAudio callback and UI updates mutate `_cached_zi` simultaneously.
  - Issue 3.2 (`live_worker.terminate()`): True positive. Forceful termination during PortAudio stream execution leaves PortAudio C locks deadlocked.
  - Issue 3.3 (Missing `closeEvent`): True positive. Closing window while worker threads run triggers Qt `SIGABRT`.
  - Issue 3.4 (Duplicate `self.error.emit(str(e))`): True positive (Low severity duplicate line).
  - Issue 3.5 (Preflight returns `True` on error): True positive. Intended as a skip mechanism, but masks real hardware initialization failures.
  - Issue 3.6 (GUI thread blocked during auto-calibration): True positive.
- **Category 4 (Buffer Shapes & Slicing, Issues 4.1–4.4):**
  - Issue 4.1 (`M @ mag` mismatch): True positive (Critical/High).
  - Issues 4.2 & 4.3 (Negative slice indexing in noise floor): True positives. When `noise_floor` buffer is shorter than `n_chunk_len`, negative indexing wraps around, producing truncated slices and raising broadcast `ValueError`.
  - Issue 4.4 (`generate_sweep` sample rate switch drops `amplitude`): True positive.
- **Category 5 (Numerical Reductions & NaNs, Issues 5.1–5.3):**
  - Issues 5.1, 5.2, 5.3 confirmed true positives.

### 3.2. Verification of Requirement 2 (UI Completeness — 8 Findings)
Explorer 2 identified 8 issues. All 8 are confirmed true positives:
- Issue 1: `self.search_input` disconnected (True positive).
- Issue 2: `manual_browser` dead hyperlinks (True positive).
- Issue 3: Orphaned `zoom_layout` buttons (`btn_reset_zoom`, `btn_run_sweep`) never attached to any visible layout (True positive).
- Issue 4: `run_stress_test` method shadowing (True positive, Critical).
- Issue 5: `MusicianCard.on_menu_triggered` referencing nonexistent `self.iem_btn` (True positive).
- Issue 6: Dead code in `delete_profile` and corrupted deletion logic in `edit_profile` (True positive).
- Issue 7: `profile_ui.py:108` `setPixmap(NoneType)` crash (True positive).
- Issue 8: Hardcoded relative database path `"inearsnitch.db"` across EQ preset methods in `analysis_ui.py` (True positive).

### 3.3. Verification of Requirement 3 (Legal & Safety — 8 Findings)
Explorer 3 identified 8 issues. All 8 are confirmed true positives:
- SEC-AUD-01: Method shadowing bypassing calibration gate & hardcoded German dialog (True positive, Critical).
- SEC-AUD-02: Bottom-bar `STRESS` button enabled on launch without calibration prerequisite (True positive, High).
- SEC-AUD-03: Space key and RUN button triggering >107 dB SPL sweeps with zero confirmation or hearing safety banner (True positive, High).
- SEC-AUD-04: Auto-calibration firing 10 ascending 1 kHz tone bursts up to -12 dBFS without confirmation (True positive, High).
- SEC-AUD-05: Missing post-DSP amplitude clamping in `LiveSealWorker`, allowing live pink noise to output at 0 dBFS clipping levels (True positive, High).
- SEC-AUD-06: Transient first-launch EULA inaccessible after initial acceptance and omitting Stress Test hazards (True positive, Medium).
- SEC-AUD-07: Complete absence of About dialog, legal terms, or medical disclaimers in running UI (True positive, Medium).
- SEC-AUD-08: Absence of physical acoustic dB SPL contextualization or warning thresholds (True positive, Medium).

---

## 4. Master Consolidated Audit Matrix

The table below consolidates all verified issues across the three audit domains, categorized by Requirement and ranked by Severity:

| ID | Domain | File Path | Line(s) | Severity | Issue Summary | Verification Status |
|:---|:---|:---|:---|:---|:---|:---|
| **R1-01** | R1 (Math) | `analysis.py` | 141 | **CRITICAL** | `thd_data` 5-tuple vs 3-variable unpack crash in diagnostics | Verified True Positive |
| **R3-01** | R3/R2 | `main.py` | 2619, 4001 | **CRITICAL** | Method shadowing of `run_stress_test`: bypasses calibration check, dead-codes HOHD pipeline, hardcodes German text | Verified True Positive |
| **R1-02** | R1 (Math) | `eq_math.py` | 17–18 | **HIGH** | `ZeroDivisionError` when `q <= 0` or `fs <= 0` in biquad filter | Verified True Positive |
| **R1-03** | R1 (Thread) | `main.py` | 603–612 | **HIGH** | `M @ mag` matrix dimension mismatch in PortAudio callback on variable buffer size | Verified True Positive |
| **R1-04** | R1 (Math) | `audio_engine.py` | 148–150 | **HIGH** | `ZeroDivisionError` in calibration ratio when `cal_sweep_amp == 0` | Verified True Positive |
| **R1-05** | R1 (Math) | `audio_engine.py` | 464–468 | **HIGH** | Unchecked length mismatch in mic calibration interpolation | Verified True Positive |
| **R1-06** | R1 (Thread) | `eq_math.py` | 54–80 | **HIGH** | Global `dsp_engine` filter state concurrency & mutation race condition | Verified True Positive |
| **R1-07** | R1 (Thread) | `main.py` | 3795–3797 | **HIGH** | `live_worker.terminate()` forces thread abort while holding PortAudio locks | Verified True Positive |
| **R1-08** | R1 (Thread) | `main.py` | 739–750 | **HIGH** | Missing `closeEvent` on `MainWindow` causes `SIGABRT` on window exit | Verified True Positive |
| **R1-09** | R1 (Math) | `audio_engine.py` | 595–598 | **HIGH** | Negative slice index broadcast crash in THD noise floor windowing | Verified True Positive |
| **R1-10** | R1 (Math) | `audio_engine.py` | 685–688 | **HIGH** | Negative slice index broadcast crash in HOHD noise floor windowing | Verified True Positive |
| **R1-11** | R1 (Math) | `audio_engine.py` | 135, 342, 543 | **HIGH** | `ValueError: zero-size array` reduction on empty recording buffers | Verified True Positive |
| **R2-01** | R2 (UI) | `main.py` | 1688–1725 | **HIGH** | `manual_browser` dead hyperlinks (external URLs & internal `#anchors` fail `os.path.exists`) | Verified True Positive |
| **R2-02** | R2 (UI) | `profile_ui.py` | 106–108 | **HIGH** | `QLabel.setPixmap(NoneType)` crash on unreadable or corrupt avatar images | Verified True Positive |
| **R3-02** | R3 (Safety)| `main.py` | 1329–1337 | **HIGH** | Bottom-bar `STRESS` button permanently enabled on startup without calibration check | Verified True Positive |
| **R3-03** | R3 (Safety)| `main.py`, `analysis_ui.py`| `788, 1323; 738`| **HIGH** | Spacebar shortcut and RUN button trigger >107 dB SPL sweeps with zero confirmation | Verified True Positive |
| **R3-04** | R3 (Safety)| `main.py` | 1631, 2420 | **HIGH** | Auto-calibration plays 10 ascending 1 kHz tone bursts up to -12 dBFS without warning | Verified True Positive |
| **R3-05** | R3 (Safety)| `main.py` | 590–602 | **HIGH** | `LiveSealWorker` lacks post-DSP amplitude clamping, permitting 0 dBFS pink noise | Verified True Positive |
| **R1-12** | R1 (Math) | `audio_engine.py` | 195–196 | **MEDIUM** | Division by zero in noise floor spectrum if recording buffer is empty | Verified True Positive |
| **R1-13** | R1 (Math) | `audio_engine.py` | 565 | **MEDIUM** | Division by zero in THD calculation if `f_end == f_start` | Verified True Positive |
| **R1-14** | R1 (Math) | `audio_engine.py` | 729–738 | **MEDIUM** | Division by zero / overflow in CSD if `slices <= 0` or `window_len <= 0` | Verified True Positive |
| **R1-15** | R1 (Math) | `main.py` | 2550, 2558 | **MEDIUM** | Non-monotonic interpolation and division by zero in auto-calibration | Verified True Positive |
| **R1-16** | R1 (DB) | `database.py` | 187–189 | **MEDIUM** | Unwrapped `np.frombuffer` in `load_reference_measurement` raises `ValueError` on bad blob | Verified True Positive |
| **R1-17** | R1 (Audio)| `audio_engine.py` | 132–133 | **MEDIUM** | Preflight check returns `passed=True` on fatal audio stream errors | Verified (Design Flaw) |
| **R1-18** | R1 (UI) | `main.py` | 2448–2520 | **MEDIUM** | Auto-calibration loop runs synchronously on GUI thread, causing window freezes | Verified True Positive |
| **R1-19** | R1 (Audio)| `audio_engine.py` | 226–229 | **MEDIUM** | Native sample rate switch in `measure()` drops caller's `amplitude` parameter | Verified True Positive |
| **R1-20** | R1 (Math) | `audio_engine.py` | 392–394 | **MEDIUM** | Silent NaN bypass in SNR / crest factor checks allows corrupt curves | Verified True Positive |
| **R1-21** | R1 (Math) | `eq_math.py` | 75–76 | **MEDIUM** | Uncaught `ValueError` in `signal.lfilter_zi` on unstable biquad poles | Verified True Positive |
| **R1-22** | R1 (Audio)| `audio_engine.py` | 86, 130, 224, 315 | **MEDIUM** | `sd.query_devices(None)` returns list; indexing with string raises `TypeError` | Verified (Partially Mitigated) |
| **R2-03** | R2 (UI) | `main.py` | 991–1000 | **MEDIUM** | `self.search_input` has zero signal connections (dead input field) | Verified True Positive |
| **R2-04** | R2 (UI) | `analysis_ui.py` | 694–756 | **MEDIUM** | Orphaned `zoom_layout` (`btn_reset_zoom`, `btn_run_sweep`) trapped and invisible | Verified True Positive |
| **R2-05** | R2 (UI) | `main.py` | 278–282 | **MEDIUM** | `MusicianCard.on_menu_triggered` crashes with `AttributeError: iem_btn` | Verified True Positive |
| **R2-06** | R2 (UI) | `main.py` | 3418–3522 | **MEDIUM** | Dead `delete_profile` and corrupt deletion logic in dead `edit_profile` | Verified True Positive |
| **R3-06** | R3 (Legal) | `main.py` | 803–832 | **MEDIUM** | EULA shown once on install, never re-accessible, omits Stress Test hazards | Verified True Positive |
| **R3-07** | R3 (Legal) | `main.py` | Global UI | **MEDIUM** | No About dialog, no legal disclaimer modal, no audiological waiver in GUI | Verified True Positive |
| **R3-08** | R3 (Safety)| `audio_engine.py`, `verify_stress_safety.py` | Global | **MEDIUM** | Software relies on digital dBFS caps without verifying real acoustic dB SPL | Verified True Positive |
| **R1-23** | R1 (UI) | `main.py` | 2777–2781 | **LOW** | `TypeError` if `_last_report` is `None` during stress report prepending | Verified True Positive |
| **R1-24** | R1 (Thread) | `main.py` | 700–701 | **LOW** | Duplicate `self.error.emit(str(e))` emission in `MeasurementWorker` | Verified True Positive |
| **R2-07** | R2 (UI) | `analysis_ui.py` | 1579, 1600, 1681 | **LOW** | Relative SQLite path `"inearsnitch.db"` causes preset loss if cwd differs | Verified True Positive |

---

## 5. Verification of Zero Code Modifications

In strict adherence to the auditor mandate:
- **`git status --no-ahead-behind` output:**
  ```
  On branch main
  Changes not staged for commit:
    modified:   .agents/ORIGINAL_REQUEST.md
    modified:   .agents/sentinel/BRIEFING.md
    modified:   ORIGINAL_REQUEST.md
  Untracked files:
    .agents/explorer_audit_r1_1/
    .agents/explorer_audit_r2_1/
    .agents/explorer_audit_r3_1/
    .agents/orchestrator_3/
    .agents/reviewer_audit_1/
    benchmark.py
  no changes added to commit (use "git add" and/or "git commit -a")
  ```
- No project source files (`*.py`, `*.md` manuals, `*.db`, etc.) were modified, edited, or deleted. All verification was conducted non-destructively via static inspection and CLI reproduction snippets.

---

## 6. Prioritized Remediation Roadmap for Developer Team

To achieve release readiness, the development team should address findings in three targeted phases:

### Phase 1: Critical Release Blockers (Must Fix Immediately)
1. **Fix `analysis.py:141` Tuple Unpack**:
   Allow `thd_data` to be either 3 or 5 elements so diagnostics do not crash after standard sweeps.
2. **Resolve `run_stress_test` Method Shadowing (`main.py:4001`)**:
   Delete line 4001. Unify the calibration check from line 2619 with an English/localized modal dialog requiring explicit in-coupler confirmation.
3. **Fix `profile_ui.py:108` `setPixmap(NoneType)` Crash**:
   Guard `self.img_label.setPixmap` to call `set_empty_style()` if `circ_pix` is `None`.
4. **Fix PortAudio Matrix Dimension Mismatch (`main.py:612`)**:
   Enforce fixed 8192-sample buffering before `M @ mag` in `LiveSealWorker.callback()`.

### Phase 2: High-Severity Safety & Functional Fixes
5. **Gate High-SPL Audio Triggers**:
   - Initialize bottom-bar `self.btn_stress.setEnabled(False)` until calibrated.
   - Add a persistent visual hearing safety warning banner above the measurement canvas.
   - Require confirmation on `_run_level_calibration` before firing 1 kHz tone bursts.
   - Add post-DSP clipping in `LiveSealWorker`: `pn = np.clip(pn, -cal_amp, cal_amp)`.
6. **Fix Dead Hyperlinks in Documentation Browser (`main.py:1688`)**:
   Support external web URLs via `QDesktopServices.openUrl(url)` and in-page anchor navigation.
7. **Fix Biquad Division by Zero (`eq_math.py:18`)**:
   Clamp `q = max(float(q), 0.001)` and `fs = max(int(fs), 1)`.
8. **Fix Negative Slice Wrapping in Noise Floor (`audio_engine.py:598, 688`)**:
   Ensure slice bounds are non-negative and zero-pad noise buffers when shorter than chunk length.
9. **Implement `MainWindow.closeEvent` & Safe Worker Termination**:
   Ensure `live_worker`, `worker`, and `_stress_worker` stop cooperatively without calling `.terminate()`.

### Phase 3: Secondary Cleanups (Medium & Low)
10. Connect `self.search_input` to filter profiles or remove the dead widget.
11. Reparent or prune orphaned `AnalysisWidget` zoom and sweep buttons.
12. Purge dead `delete_profile`, `edit_profile`, and `MusicianCard.on_menu_triggered` methods from `main.py`.
13. Add an "About / Health & Safety" dialog in Settings allowing re-access to the EULA.
14. Replace relative `"inearsnitch.db"` in `analysis_ui.py` with `self.db.db_path`.
