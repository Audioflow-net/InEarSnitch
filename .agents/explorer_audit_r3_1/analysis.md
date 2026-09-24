# Legal & Safety Audit Report: Health & Safety Disclaimers & Hearing Protection

**Audit Date**: 2026-09-24  
**Auditor**: `explorer_audit_r3_1` (teamwork_preview_explorer)  
**Project**: InEar Snitch (IEC-711 IEM Acoustic Measurement Tool)  
**Target Scope**: Legal compliance, hearing damage risks, high-SPL safety gates (+15dB Stress Test, sine sweeps, auto-calibration, pink noise), and liability disclaimers across `main.py`, `audio_engine.py`, `analysis_ui.py`, `calibration_ui.py`, and documentation.

---

## 1. Executive Summary

InEar Snitch is an acoustic measurement tool interfacing directly with physical audio interfaces, IEC-711 reference couplers, and high-sensitivity In-Ear Monitors (IEMs). During logarithmic sine sweeps and high-level "Stress Tests", sound pressure levels (SPL) routinely exceed **105 to 115+ dB SPL** (and can easily exceed **125–130 dB SPL** if audio interface gain is high or Balanced Armature IEMs are attached). Exposure to such levels inside an ear canal causes **immediate, irreversible acoustic trauma, permanent hearing damage, and severe tinnitus**.

This audit revealed **critical structural vulnerabilities and safety omissions**:
1. **Critical Method Shadowing**: `main.py` defines `run_stress_test()` twice (lines 2619 and 4001). The second definition overwrites the first, bypassing the calibration safety gate entirely and displaying a warning **hardcoded exclusively in German** within an otherwise English UI.
2. **Accidental Triggering of Extreme SPL**: The bottom-bar "STRESS" button is permanently enabled on startup right next to the normal RUN button without requiring prior level calibration or safe-SPL staging.
3. **Zero Safety Gates on Normal Sweeps**: Normal sine sweeps (up to 107+ dB SPL) and keyboard shortcuts (`Space`) trigger high-output audio instantly with zero confirmation, no coupler check, and no persistent hearing protection banner.
4. **Unprotected Auto-Calibration**: Settings Auto-Calibration immediately fires 10 escalating 1 kHz sine bursts (up to -12 dBFS) without asking the user to confirm the IEM is in the coupler.
5. **DSP Clipping Hazard in Live Pink Noise**: `LiveSealWorker` lacks post-DSP amplitude clamping, permitting boosted EQ signals to stream at full digital scale (0 dBFS).
6. **Hidden Disclaimers**: The EULA is shown once on first launch and cannot be re-opened anywhere in the UI. There is no About dialog, no legal disclaimer view, and no medical/audiological waiver accessible during operation.

---

## 2. Inventory of Occurrences

| Search Query | Files & Occurrences | Context & Role |
| :--- | :--- | :--- |
| **"Stress Test" / "STRESS"** | `main.py:1329, 2613-2625, 2673-2689, 4001-4011`<br>`analysis_ui.py:651, 817-825, 1153-1157`<br>`verify_stress_safety.py:4, 18, 67`<br>`manual_en.md:230, 246, 252`<br>`manual_de.md:232, 248, 254`<br>`HOW_TO_START_AGENT_BRIEFING.md:60, 63` | UI buttons, worker invocation, THD/HOHD Rub & Buzz detection, user manuals |
| **"+15dB" / "15dB" / "15 dB"** | `main.py:4004`<br>`main.py:2527, 2535, 3842`<br>`manual_en.md:24 (patch)`<br>`manual_de.md:25 (patch)` | Claimed stress level boost in German dialog, target recording peak (-15 dBFS), filter clog detection threshold (-15 dB) |
| **"stress_test"** | `main.py:643, 653, 663, 4011, 4013, 4083`<br>`analysis_ui.py:819-825` | Parameter in `MeasurementWorker` and `run_measurement()` |
| **Sweep Generation** | `audio_engine.py:15-46 (`generate_sweep`)`<br>`audio_engine.py:54-90 (`preflight_check`)`<br>`audio_engine.py:200-290 (`measure`)`<br>`main.py:2444-2464 (`_run_level_calibration`)` | Logarithmic chirp synthesis, 1 kHz preflight tone, ascending calibration bursts |
| **"hearing" / "Gehör" / "EULA"** | `main.py:803-832 (`check_eula`)`<br>`manual_en.md:226-234`<br>`manual_de.md:228-236`<br>`manual_es.md:217-225`<br>`HOW_TO_START_AGENT_BRIEFING.md:21-25` | Initial startup warning dialog, Section 10 of manuals |

---

## 3. Detailed Audit Findings & Issues

### Issue 1: Method Shadowing Bypasses Calibration Safety Gate and Hardcodes German Text
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines**: 2619–2726 (Definition 1) vs 4001–4012 (Definition 2)
- **Code Snippet**:
  ```python
  # Line 2619:
  def run_stress_test(self):
      """Run a high-amplitude sweep and extract HOHD for Rub & Buzz detection."""
      stress_amp = getattr(self.audio_engine, 'calibrated_stress_amp', None)
      if stress_amp is None:
          QMessageBox.warning(self, "Not Calibrated Yet",
                              "Please run Output Level Calibration first (in Settings → Calibration) before using the Stress Test.")
          return
      ...
  
  # Line 4001:
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
- **Nature of Safety & Legal Violation**:
  1. **Python Method Shadowing**: In Python, defining a method twice in the same class causes the second definition to overwrite the first. Definition 2 (line 4001) silently overwrites Definition 1 (line 2619).
  2. **Bypasses Calibration Safety Gate**: Definition 1 enforced that `self.audio_engine.calibrated_stress_amp` was not `None`. Definition 2 contains no calibration check whatsoever. An uncalibrated user can immediately trigger the stress sweep at an uncontrolled hardware interface output volume.
  3. **Critical Internationalization / Safety Hazard**: The rest of the application UI is in English. Definition 2 hardcodes the safety-critical prompt entirely in German (`"ACHTUNG: STRESS TEST"`, `"Nimm den In-Ear auf JEDEN FALL aus deinem Ohr!"`). English-, Spanish-, or non-German-speaking users cannot comprehend this urgent instruction, significantly increasing the probability of wearing the IEM during the high-SPL test.
  4. **Misleading Level Specification & Dead Code**: The dialog warns of `+15dB`, but line 4001 calls `run_measurement(is_stress_test=True)` which in `MeasurementWorker:663` only applies `amplitude = 0.25` (vs `0.15` normal, a +4.4 dB increase). The intended Rub & Buzz HOHD extraction worker (`StressWorker`) and preflight stress checks in Definition 1 are completely dead code.
- **Severity**: **Critical**
- **Recommended Remediation**:
  1. Remove the shadowed second definition at line 4001.
  2. In Definition 1 (line 2619), replace `QMessageBox.question` with a prominent bilingual/localized modal dialog styled as a critical hazard warning.
  3. Enforce the calibration prerequisite (`if stress_amp is None:`).
  4. Require explicit acknowledgement (e.g. checkbox: *"I confirm the IEM is inserted in the coupler and not in any ear"*).

---

### Issue 2: Bottom-Bar "STRESS" Button Permanently Enabled Without Calibration Prerequisite
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines**: 1329–1337
- **Code Snippet**:
  ```python
  self.btn_stress = QPushButton("STRESS")
  self.btn_stress.setToolTip("Run high-level Rub & Buzz sweep")
  self.btn_stress.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
  self.btn_stress.setFixedWidth(80)
  self.btn_stress.setStyleSheet("QPushButton { background-color: #ef4444; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; padding: 12px 5px;} QPushButton:disabled { background-color: #333; color: #666; } QPushButton:hover { background-color: #f87171; }")
  self.btn_stress.clicked.connect(self.run_stress_test)
  run_layout.addWidget(self.btn_stress)
  ```
- **Nature of Safety & Legal Violation**:
  1. While the stress test button in the Analysis THD tab (`page_ana.btn_stress_test` in `analysis_ui.py:820`) is safely initialized with `setEnabled(False)` until Output Level Calibration is completed, this prominent bright red button on the main bottom bar is **permanently enabled on app launch**.
  2. It is placed directly adjacent to the main `RUN` button (`self.btn_capture`), inviting accidental clicks.
  3. Its tooltip (`"Run high-level Rub & Buzz sweep"`) contains **zero safety warning**, no mention of extreme SPL, and no warning against in-ear insertion.
- **Severity**: **High**
- **Recommended Remediation**:
  1. Initialize `self.btn_stress.setEnabled(False)` in `main.py:1330`.
  2. Only enable `self.btn_stress` when `self.audio_engine.calibrated_stress_amp` is set via successful Output Level Calibration.
  3. Update tooltip to: `"High-SPL stress test (+6 to +15 dB). NEVER wear IEMs during test. Requires Output Level Calibration."`
  4. Visually separate or gate the button behind a confirmation switch to prevent misclicks next to `RUN`.

---

### Issue 3: Zero Hearing Protection Confirmation or Visual Gate on Normal Sine Sweeps
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py` and `/Users/ben/Desktop/InEarSnitch/analysis_ui.py`
- **Lines**: `main.py:788`, `1323–1327`, `4013–4061`; `analysis_ui.py:738–741`
- **Code Snippet**:
  ```python
  # main.py:788
  QShortcut(QKeySequence("Space"), self).activated.connect(self.btn_capture.click)
  
  # main.py:1323-1327
  self.btn_capture = QPushButton("RUN")
  self.btn_capture.setToolTip("Start measurement capture (Space)")
  self.btn_capture.clicked.connect(self.run_measurement)
  
  # analysis_ui.py:738-741
  self.btn_run_sweep = QPushButton("▶ MEASURE")
  self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
  ```
- **Nature of Safety & Legal Violation**:
  1. Logarithmic sine sweeps across 5 Hz – 24 kHz produce ~107 dB SPL at standard test amplitudes (as documented in `verify_stress_safety.py:74`), and easily exceed 115–120 dB SPL with sensitive IEMs or loud interface settings.
  2. A normal sweep is triggered instantly upon clicking `RUN`, clicking `▶ MEASURE`, or accidentally tapping the `Space` key on the keyboard.
  3. There is **zero confirmation**, **zero in-coupler verification**, and **no warning indicator** anywhere on the measurement page. If a musician puts their custom in-ear into their ear to check if audio works, an accidental Space keypress can trigger an instant full-amplitude sine sweep directly into their ear canal.
- **Severity**: **High**
- **Recommended Remediation**:
  1. Add a persistent, prominent warning banner above the measurement graph:  
     `⚠️ HEARING SAFETY: Acoustic sweeps exceed 105 dB SPL. NEVER wear IEMs during measurement. Coupler use only.`
  2. Require a confirmation prompt on the first sweep of each session with a checkbox: `[ ] Do not show again for this session`.
  3. Remove or gate the global `Space` shortcut (e.g. require `Ctrl+Space` or disable shortcut unless explicitly enabled in Settings).

---

### Issue 4: Settings Auto-Calibration Plays Ascending 1 kHz Sine Bursts (Up to -12 dBFS) Without Confirmation
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines**: 1631–1635, 2420–2526
- **Code Snippet**:
  ```python
  # Lines 1631-1634:
  self.btn_auto_cal = QPushButton("Start Auto-Calibration")
  self.btn_auto_cal.clicked.connect(self._run_level_calibration)
  
  # Lines 2444-2453:
  steps = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20, 0.25]
  results = []
  log_lines = []
  
  for amp in steps:
      try:
          n = int(0.2 * self.audio_engine.sample_rate)
          t = np.linspace(0, 0.2, n, False)
          tone = np.sin(2 * np.pi * 1000 * t) * amp
  ```
- **Nature of Safety & Legal Violation**:
  1. Clicking "Start Auto-Calibration" in Settings → Calibration immediately begins blasting 10 ascending 1 kHz pure sine bursts into the audio output, reaching up to 0.25 digital amplitude (-12 dBFS).
  2. 1 kHz pure tones at high volume represent high acoustic energy and acute hazard for human hearing.
  3. There is no pre-calibration warning or confirmation dialog verifying that the IEM is mounted in the coupler and removed from human ears.
- **Severity**: **High**
- **Recommended Remediation**:
  1. Insert a modal confirmation dialog before `_run_level_calibration` starts:
     ```python
     reply = QMessageBox.warning(
         self, "Start Output Level Calibration?",
         "This calibration will play 10 escalating 1 kHz tones up to high volume.\n\n"
         "• Make sure the IEM is securely seated inside the coupler.\n"
         "• NEVER wear the IEM in your ears during calibration!\n\n"
         "Do you want to start calibration now?",
         QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel
     )
     if reply != QMessageBox.Ok:
         return
     ```

---

### Issue 5: Live RTA / Depth Guide Streams Continuous Pink Noise Without Post-DSP Clipping Protection
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines**: 534–536, 590–602, 1296–1312, 3715–3790
- **Code Snippet**:
  ```python
  # Line 534-536:
  cal_amp = getattr(self, '_cal_amp', 0.15)
  pink_noise_full = (y / np.max(np.abs(y))) * cal_amp
  
  # Line 590-595:
  from eq_math import dsp_engine
  if dsp_engine.master_enabled:
      pn = dsp_engine.process(pn, self.fs)
      # MISSING: np.clip(pn, -cal_amp, cal_amp)
      
  if self.target_channel == "Left":
      outdata[:, 0] = pn
  ```
- **Nature of Safety & Legal Violation**:
  1. Toggling "RTA" or "Depth" starts an indefinite audio stream playing continuous pink noise through the IEM.
  2. Tooltips (`"Start Raw Live RTA"`, `"Live RTA: Align 8kHz Resonance Peak (Insertion Depth)"`) provide no notification that loud audio playback will commence immediately.
  3. While `audio_engine.py:43` explicitly includes safety clipping (`sweep = np.clip(sweep, -amplitude, amplitude)`) after DSP processing to avoid over-excursing Balanced Armature drivers, `LiveSealWorker.run()` at line 592 omits this clamp! If the DSP Engine has active EQ boosts (+12 dB), the pink noise will stream at digital clipping levels (up to 0.99 amplitude / 0 dBFS), creating severe acoustic exposure and thermal driver destruction risks.
- **Severity**: **High**
- **Recommended Remediation**:
  1. Add post-DSP safety clipping in `LiveSealWorker.run`:  
     `pn = np.clip(pn, -cal_amp, cal_amp)`
  2. Update button tooltips to clearly indicate continuous audio playback:  
     `"Live RTA: Plays continuous pink noise through IEM into coupler to guide 8kHz insertion depth. Coupler only."`

---

### Issue 6: EULA / Health & Safety Disclaimer Displayed Only Once on First Launch With No Re-Access
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py`
- **Lines**: 803–832
- **Code Snippet**:
  ```python
  s = QSettings("InEarSnitch", "InEarSnitchApp")
  if not s.value("eula_accepted", False, type=bool):
      msg = QMessageBox(self)
      msg.setWindowTitle("Health & Safety Warning")
      msg.setIcon(QMessageBox.Warning)
      msg.setText("<b>WARNING: High-Level Sine Sweeps</b>")
      msg.setInformativeText(
          "This software generates loud, high-frequency audio sweeps which can cause <b>permanent hearing damage</b> "
          "if listened to directly, or <b>hardware damage</b> (blown drivers) if the output level is incorrectly staged.<br><br>"
          "• NEVER wear the In-Ear Monitors (IEMs) while running a measurement.<br>"
          "• ALWAYS double-check your audio interface output volume before clicking RUN.<br><br>"
          "By clicking 'Accept', you confirm you understand these risks and release the developers of InEar SNITCH from any liability regarding hearing loss or equipment damage.<br><br>"
          "This software does not provide medical or audiological advice. Measurement results are for informational purposes only and must not be used for medical diagnosis or treatment decisions."
      )
      ...
      if ret == QMessageBox.Ok:
          s.setValue("eula_accepted", True)
          s.sync()
  ```
- **Nature of Safety & Legal Violation**:
  1. Once accepted on initial installation, the flag `eula_accepted = True` is stored in QSettings and the dialog is never shown again.
  2. There is no menu item, button, or link in Settings or Help allowing a user, laboratory supervisor, or secondary technician to review the Health & Safety terms or liability waiver.
  3. The disclaimer text at line 815 specifically discusses general sine sweeps, but completely omits mention of the high-SPL (+15dB) Stress Test and Rub & Buzz procedures.
- **Severity**: **Medium**
- **Recommended Remediation**:
  1. Add a "Health & Safety / Legal Terms" button in Settings and in the top-bar menu.
  2. Allow resetting or reviewing the EULA at any time.
  3. Update the EULA text to explicitly mention Stress Tests and high-amplitude harmonic distortion testing.

---

### Issue 7: Complete Absence of About Dialog, Legal Disclaimer Page, or Liability Terms in UI
- **File**: `/Users/ben/Desktop/InEarSnitch/main.py` (and entire codebase)
- **Lines**: Entire UI layout
- **Nature of Safety & Legal Violation**:
  1. InEar Snitch has no "About" box, no legal disclaimer modal, and no dedicated Safety tab.
  2. The only legal notice in `SettingsPanel` is a 2-line local storage privacy statement at line 1822:
     `"Privacy: All data (musician profiles, measurements, photos) is stored exclusively on this device..."`
  3. While Chapter 10 of `manual_en.md`, `manual_de.md`, and `manual_es.md` contains comprehensive safety warnings, this content is buried in the 4th subtab of an overlay panel behind Markdown documentation links.
  4. From a legal liability standpoint, critical warnings regarding physical injury (hearing damage) must be visible in the primary operational flow of the software.
- **Severity**: **Medium**
- **Recommended Remediation**:
  1. Add an "About & Legal" dialog accessible from the top bar (near Settings).
  2. Include clear developer liability waivers, hearing health warnings, and explicit statements that InEar Snitch is not a medical device.

---

### Issue 8: Inadequate Safe-Listening Decibel Scale Contextualization
- **File**: `/Users/ben/Desktop/InEarSnitch/audio_engine.py` and `/Users/ben/Desktop/InEarSnitch/verify_stress_safety.py`
- **Lines**: `audio_engine.py:20, 24, 43`; `verify_stress_safety.py:73–84`
- **Code Snippet**:
  ```python
  # audio_engine.py:20-24
  # Hard-capped at 0.25 (-12 dBFS) for IEM safety.
  amplitude = min(amplitude, 0.25)
  
  # verify_stress_safety.py:74-81
  est_spl_normal = 107  # dB SPL at amplitude 0.1 (conservative estimate)
  est_spl_stress = est_spl_normal + target_boost_db
  if est_spl_stress > 114:
      print("🔴 ÜBER 114 dB! Gefahr für BA-Hochtöner!")
  ```
- **Nature of Safety & Legal Violation**:
  1. Digital attenuation (`amplitude <= 0.25`) is an incomplete safety measure because acoustic sound pressure level in the physical world depends on analogue interface gain and IEM sensitivity (dB SPL per mW).
  2. The developer notes in `verify_stress_safety.py` that normal sweeps produce ~107 dB SPL and stress sweeps exceed 114 dB SPL. Under OSHA and NIOSH occupational standards, 115 dB SPL carries immediate risk of acoustic trauma without hearing protection.
  3. The user interface provides no estimated SPL readout, no visual dB meter, and no indicator warning when an output configuration produces dangerous sound pressure levels.
- **Severity**: **Medium**
- **Recommended Remediation**:
  1. If SPL calibration has been performed (via `spl_cal_ui.py`), display the estimated peak SPL alongside the measurement status.
  2. Show a red warning badge when estimated SPL exceeds 100 dB SPL.

---

## 4. Summary Table of Audit Issues

| Issue ID | Severity | File Path | Line Number(s) | Violation Nature |
| :--- | :--- | :--- | :--- | :--- |
| **SEC-AUD-01** | **Critical** | `main.py` | 2619, 4001 | Method redefinition shadows calibration check, dead-codes HOHD analysis, hardcodes warning in German |
| **SEC-AUD-02** | **High** | `main.py` | 1329–1337 | Bottom-bar "STRESS" button permanently enabled on launch without calibration gate or safety tooltip |
| **SEC-AUD-03** | **High** | `main.py`, `analysis_ui.py` | `main.py:788, 1323, 4013`; `analysis_ui.py:738` | Normal sweeps and Space shortcut trigger >107 dB SPL with zero confirmation or hearing warning |
| **SEC-AUD-04** | **High** | `main.py` | 1631–1635, 2420–2526 | Auto-calibration immediately plays 10 escalating 1 kHz tones up to -12 dBFS without warning |
| **SEC-AUD-05** | **High** | `main.py` | 534–536, 590–602 | `LiveSealWorker` lacks post-DSP amplitude clamping, permitting 0 dBFS pink noise with active EQ boosts |
| **SEC-AUD-06** | **Medium** | `main.py` | 803–832 | Health & Safety EULA displayed only once on first launch; cannot be re-opened; omits Stress Test risks |
| **SEC-AUD-07** | **Medium** | `main.py` | Global UI | No About dialog, no legal disclaimer page, no medical/audiological waiver accessible during operation |
| **SEC-AUD-08** | **Medium** | `audio_engine.py`, `verify_stress_safety.py` | `audio_engine.py:20`; `verify_stress_safety.py:73` | Software relies on digital dBFS caps without verifying real-world physical acoustic dB SPL limits |

---

## 5. Verification Method

To verify these findings independently without altering the repository:
1. **Method Redefinition**: Inspect `main.py` with `grep -n "def run_stress_test" main.py`. Note lines 2619 and 4001. Execute Python inspection:
   ```bash
   python3 -c "import main; print(main.MainWindow.run_stress_test.__doc__)"
   ```
   Observed output: `None` (because the docstring on line 2620 was overwritten by line 4001 which has no docstring).
2. **Bottom-Bar Button State**: Launch the GUI or inspect line 1329: `self.btn_stress = QPushButton("STRESS")`. Note absence of `self.btn_stress.setEnabled(False)` compared to `analysis_ui.py:820`.
3. **Spacebar Shortcut**: Observe line 788: `QShortcut(QKeySequence("Space"), self).activated.connect(self.btn_capture.click)`.
4. **Auto-Calibration Tone Burst**: Inspect line 1634: `self.btn_auto_cal.clicked.connect(self._run_level_calibration)` and observe lines 2420–2460 where `sd.Stream` is immediately started with no `QMessageBox`.
5. **DSP Clamping in LiveSealWorker**: Inspect lines 590–602 of `main.py` vs lines 38–44 of `audio_engine.py`. Observe absence of `np.clip` in `LiveSealWorker`.
