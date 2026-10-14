# INEAR SNITCH - MASTER ARCHITECTURE & DSP LORE

**MANDATORY READING FOR ALL AGENTS:** 
This document contains the core physics, DSP hacks, and architectural realities of this project. If you try to "refactor" or "optimize" code without understanding this lore, you will break the app for live stage usage.

## 1. THE CORE PHILOSOPHY ("Stumpf & Schnell")
This is a Pro-Audio tool designed to be used by Sound Engineers in high-stress, extremely loud environments (e.g., 115 dB EDM festival stages). 
- **Rule:** Do not add "Are you sure?" pop-ups to standard workflows. The UI must be fast, responsive, and robust.

## 2. DSP & PHYSICS REALITIES (Do not "fix" these!)

### A. macOS Voice Isolation & Cheap ADCs (The 1kHz Drop)
On a loud EDM stage, cheap ADCs (like AliExpress mic inputs) buckle under the bass, and macOS features like "Voice Isolation" or "Auto-Gain" aggressively compress the signal.
- **The Hack:** The `preflight_check` (which plays a 1kHz tone) will often see the tone drop by 15-20 dB compared to calibration. The background noise floor might read as dead silent (-82 dBFS) because Apple AI deletes the stage noise. 
- **Agent Rule:** Do NOT tighten the dB drift tolerances in `preflight_check`. The logic intentionally accepts these massive drops and handles them via a smart UX text warning ("Volume Mismatch or Stage Noise?"), allowing the user to measure anyway.

### B. The RTA "Chicken & Egg" Problem (Pink Noise)
The `LiveSealWorker` (Depth Check) starts playing Pink Noise *instantly* without a mathematical volume pre-check. 
- **The Hack:** This is intentional. The user opens the RTA *because* they need to seat the IEM in the coupler. If we ran a volume check before the RTA, it would always fail (since the IEM isn't sealed yet and sound bleeds out). The RTA *must* run blindly. 
- **Agent Rule:** Never attempt to add a mathematical audio check before starting the `LiveSealWorker`. The only safety net allowed is a UI text warning.

### C. Farina Sweep vs. EDM Bass (THD Artifacts)
Stage bass will completely ruin THD (Total Harmonic Distortion) calculations, showing absurd values like 38%. However, Angelo Farina's Log-Sweep deconvolution perfectly separates the Frequency Response from the uncorrelated stage noise. 
- **Physics facts to know:** Balanced Armature (BA) drivers have almost zero mechanical excursion. High THD in the sub-bass (50 Hz) is a physical reality at high volumes, not a software bug. THD spikes at 300-500 Hz in Multi-BA setups are normal electrical crossover humps.

## 3. PYQT ARCHITECTURE & THREADING RULES

### A. The Anti-Beachball Rule (No Blocking Waits)
Audio operations (like `sd.Stream`) must never use a blocking `event.wait(1.0)` on the Main GUI Thread. This causes the macOS spinning beachball and freezes the UI.
- **The Hack:** If you must wait synchronously on the main thread, use this micro-sleep loop:
  ```python
  start_wait = time.time()
  while not event.is_set() and (time.time() - start_wait < 1.0):
      event.wait(timeout=0.02)
      QApplication.processEvents()
  ```

### B. Worker Shutdown Deadlocks
PortAudio / sounddevice can hang. If you shut down a `QThread` (e.g., in `closeEvent`), NEVER use `.wait()` without a timeout.
- **Agent Rule:** Always use `.wait(1000)` so the app can forcefully close if the audio interface hangs.

## 4. HARDWARE SAFETY & LIABILITY
- **The Stress Test (+15 dB):** This is a highly dangerous feature. If the user's physical headphone amplifier is turned up to 100%, the Stress Test sweep will OVERHEAT and MELT the BA drivers. 
- **Agent Rule:** Never remove or soften the "HARDWARE DAMAGE" / "MELT" warnings in the UI.

## 5. HARDWARE & CAD (BOM)
- Vor jeder Konstruktion zwingend die `HARDWARE_CONSTRAINTS.md` lesen (Beachte das 13 mm Limit der Überwurfmutter!).
- Jede CAD-Änderung an Adaptern oder Gehäusen MUSS in der `CHANGELOG.md` mit Begründung (altes Maß -> neues Maß) dokumentiert werden.
