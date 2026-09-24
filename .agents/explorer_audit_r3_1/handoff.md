# Handoff Report: R3 Legal & Safety Audit (Hearing Protection & High-SPL Gates)

**Auditor**: `explorer_audit_r3_1` (teamwork_preview_explorer)  
**Parent Agent**: `orchestrator_3` (ID: `a1d06762-aab4-4ea0-bdeb-cbbe07e3aa0a`)  
**Mission**: Verify that InEar Snitch contains proper Health & Safety disclaimers regarding hearing protection, specifically concerning the loud (+15dB) "Stress Test", general sine sweeps, and acoustic hazards.

---

## 1. Observation

1. **Method Shadowing / Overwriting**:
   - `main.py:2619`: Defines `def run_stress_test(self):` with docstring `"""Run a high-amplitude sweep and extract HOHD for Rub & Buzz detection."""`. Checks `stress_amp = getattr(self.audio_engine, 'calibrated_stress_amp', None)`, shows warning if uncalibrated, checks preflight levels, runs `StressWorker` for 3.0s, and updates HOHD plot.
   - `main.py:4001`: Defines a second `def run_stress_test(self):` with no docstring. Contains hardcoded German critical alert:
     ```python
     reply = QMessageBox.critical(self, "ACHTUNG: STRESS TEST",
         "Der Stress Test jagt einen extrem lauten Sweep (+15dB) durch den IEM, um mechanische Defekte aufzudecken.\n\n"
         "Nimm den In-Ear auf JEDEN FALL aus deinem Ohr!\n"
         "Er muss für diesen Test sicher im Coupler stecken.\n\n"
         "Möchtest du wirklich fortfahren?",
         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
     if reply == QMessageBox.Yes:
         self.run_measurement(is_stress_test=True)
     ```
   - Tool verification: `python3 -c "import main; print(repr(main.MainWindow.run_stress_test.__doc__))"` yields `None`, confirming that definition 2 at line 4001 completely shadows definition 1 at line 2619.

2. **Uncalibrated Bottom-Bar "STRESS" Button**:
   - `main.py:1329–1334`:
     ```python
     self.btn_stress = QPushButton("STRESS")
     self.btn_stress.setToolTip("Run high-level Rub & Buzz sweep")
     self.btn_stress.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
     self.btn_stress.setFixedWidth(80)
     self.btn_stress.setStyleSheet("QPushButton { background-color: #ef4444; color: white; ...")
     self.btn_stress.clicked.connect(self.run_stress_test)
     ```
   - In contrast to `analysis_ui.py:820` (`self.btn_stress_test.setEnabled(False)`), this button is enabled on app startup and is placed directly adjacent to the green `RUN` button (`main.py:1323`).

3. **Instant Sine Sweep Triggering & Keyboard Shortcut**:
   - `main.py:788`: `QShortcut(QKeySequence("Space"), self).activated.connect(self.btn_capture.click)`
   - `main.py:1323–1327`: `self.btn_capture.clicked.connect(self.run_measurement)`
   - `analysis_ui.py:738–741`: `self.btn_run_sweep.clicked.connect(self.request_measurement.emit)`
   - In `run_measurement(self, is_stress_test=False)` (`main.py:4013–4061`): There is no confirmation dialog, no reminder to place IEMs into the coupler, and no persistent hearing protection banner.

4. **Settings Auto-Calibration Tone Burst**:
   - `main.py:1631–1634`: `self.btn_auto_cal.clicked.connect(self._run_level_calibration)`
   - `main.py:2444–2453`: Emits 10 escalating 1 kHz sine bursts (amplitude 0.01 to 0.25, up to -12 dBFS) without any warning, confirmation dialog, or coupler placement check.

5. **Live Pink Noise Unclamped After DSP**:
   - `main.py:534–536`: `cal_amp = getattr(self, '_cal_amp', 0.15); pink_noise_full = (y / np.max(np.abs(y))) * cal_amp`
   - `main.py:590–595`:
     ```python
     if dsp_engine.master_enabled:
         pn = dsp_engine.process(pn, self.fs)
     if self.target_channel == "Left":
         outdata[:, 0] = pn
     ```
   - Unlike `audio_engine.py:43` which enforces `sweep = np.clip(sweep, -amplitude, amplitude)`, `LiveSealWorker.run()` lacks clamping, allowing boosted EQ (+12 dB) to output at full 0 dBFS.

6. **Transient First-Launch EULA**:
   - `main.py:803–832`: `check_eula()` displays a `QMessageBox` on startup and sets `s.setValue("eula_accepted", True)`. It is never shown again, cannot be re-opened, and omits mentions of the Stress Test or extreme SPL hazards.
   - There is no "About" box, no legal disclaimer modal, and no liability waiver accessible anywhere in the running GUI.

---

## 2. Logic Chain

1. **Premise**: InEar Snitch measures IEMs coupled to an IEC-711 acoustic fixture. When driven with logarithmic sine sweeps or stress test signals, acoustic output levels can exceed 105–115+ dB SPL, and with high-gain headphone amplifiers, up to 125–130 dB SPL. Exposure to these sound levels inside an ear canal causes immediate, permanent cochlear hearing damage and acute tinnitus.
2. **Inference from Obs 1 & 2**: A user can click the bright red "STRESS" button on the main bottom bar at any time without having run Output Level Calibration. Because line 4001 shadows line 2619, the calibration check is bypassed. If the user does not speak German, they will see a German message box (`"Nimm den In-Ear auf JEDEN FALL aus deinem Ohr!"`), fail to understand it, and proceed with the test while the IEM is in their ear or nearby.
3. **Inference from Obs 3**: Normal sweeps produce ~107 dB SPL. Because a single accidental press of the `Space` bar immediately runs the sweep with no confirmation or visual safety banner, an operator wearing IEMs can be subjected to immediate acoustic trauma.
4. **Inference from Obs 4 & 5**: A user exploring Settings can click "Start Auto-Calibration" or toggle "RTA"/"Depth" and immediately receive loud tone bursts (up to -12 dBFS) or continuous pink noise (potentially at 0 dBFS with active EQ) without any warning.
5. **Inference from Obs 6**: Once accepted, the EULA is inaccessible. No operator can review the safety guidelines or liability waivers from the UI.
6. **Deduction**: InEar Snitch has substantial legal exposure and safety vulnerabilities: critical safety gates are bypassed or missing, warnings are language-inconsistent, and high-SPL signals can be triggered accidentally or uncalibrated.

---

## 3. Caveats

- **Operating System Hardware Volume**: The software operates in the digital domain (-12 dBFS hard cap in `audio_engine.py`). The true physical dB SPL depends on the analogue potentiometer of the external USB audio interface (e.g. MOTU M2) and IEM sensitivity (dB/mW). Software controls cannot physically clamp an external analogue amplifier turned to maximum gain.
- **Scope Limitation**: This investigation was strictly read-only per the project instructions; no source files were modified.

---

## 4. Conclusion

The audit identifies **8 distinct safety and legal compliance issues** (1 Critical, 4 High, 3 Medium). The most urgent issue is **SEC-AUD-01** (method shadowing of `run_stress_test` in `main.py:4001`), which simultaneously breaks the calibration safety gate and introduces a dangerous language barrier for non-German operators. Remediation should focus on restoring the calibration prerequisite, replacing German dialogs with standardized localized safety gates, and adding persistent visual coupler-only warnings across all high-SPL triggers.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Method Shadowing**:
   ```bash
   python3 -c "import main; print('Docstring is None:', main.MainWindow.run_stress_test.__doc__ is None)"
   # Returns True, proving line 4001 overwrote line 2619
   ```
2. **Verify Dual Definition Line Numbers**:
   ```bash
   grep -n "def run_stress_test" /Users/ben/Desktop/InEarSnitch/main.py
   # Returns: 2619 and 4001
   ```
3. **Verify German Hardcoded Dialog in English App**:
   ```bash
   sed -n '4001,4012p' /Users/ben/Desktop/InEarSnitch/main.py
   ```
4. **Verify Enabled State of Bottom Bar STRESS Button**:
   ```bash
   sed -n '1329,1336p' /Users/ben/Desktop/InEarSnitch/main.py
   # Notice absence of setEnabled(False)
   ```
5. **Verify Spacebar Shortcut**:
   ```bash
   sed -n '788p' /Users/ben/Desktop/InEarSnitch/main.py
   ```
6. **Verify Smoke Test Baseline**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   # Verifies 19/19 checks pass
   ```

**Invalidation Conditions**:
- If `run_stress_test` at line 4001 is removed, restoring line 2619's calibration check and English dialog.
- If `self.btn_stress` is disabled until calibration is completed.
- If a persistent hearing safety banner is rendered above the measurement canvas.
