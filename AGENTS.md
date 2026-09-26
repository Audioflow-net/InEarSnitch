# AUDIO & MEASUREMENT CODE FREEZE

**CRITICAL RULE FOR ALL AGENTS WORKING IN THIS REPOSITORY:**

The user has explicitly placed a **CODE FREEZE** on all audio measurement, DSP, and diagnostic logic. 
The core audio engine is perfectly tuned, calibrated, and robust against macOS PortAudio quirks. 
**DO NOT MODIFY ANY OF THE FOLLOWING FILES OR FUNCTIONS WITHOUT EXPLICIT PERMISSION FROM THE USER:**

1. `audio_engine.py` (ALL of it. Do not touch.)
2. `main.py` -> `run_measurement()`
3. `main.py` -> `run_stress_test()`
4. `main.py` -> `_run_level_calibration()`
5. `main.py` -> `MeasurementWorker` and `StressWorker`
6. `main.py` -> `preflight_check` logic

If you are asked to work on UI, Responsive Design, CSS, layout, or packaging (e.g. PyInstaller, macOS App Bundle), you must **strictly isolate** your changes to the UI components (like `analysis_ui.py`, `profile_ui.py`, `tour_ui.py`, or the visual setup in `main.py`).

**NEVER** attempt to "refactor", "clean up", or "optimize" the audio measurement logic while working on the UI. If a UI task seems to require a change in the audio engine, STOP and ask the user for permission first.

---

# MANDATORY SMOKE TEST PROTOCOL

**Before finalizing any code change** (especially before proposing that a feature is complete or before preparing an app update), **YOU MUST RUN THE SMOKE TEST.**

Execute the following command in the terminal:
`python3 smoke_test.py`

You must ensure that **all checks pass (Exit Code 0)**. If any check fails, you must fix the regression immediately. DO NOT present the code to the user as "finished" if the smoke test is failing.
