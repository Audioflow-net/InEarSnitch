# InEar Snitch: User Manual

Welcome to InEar Snitch, the professional software for measuring, analyzing, and diagnosing In-Ear Monitors (IEMs).
This manual explains the core features and guides you through performing accurate measurements.

## Keyboard Shortcuts

The following shortcuts will speed up your workflow:
- `Space`: Run Sweep (Start Measurement)
- `Ctrl+S` / `Cmd+S`: Save Trace
- `Backspace` / `Delete`: Clear Trace
- `Ctrl+1`, `Ctrl+2`, `Ctrl+3`, `Ctrl+4`: Switch between tabs (Profile, Measurement, Analysis, History)

## 1. The User Interface (Tabs)

The application is divided into four main areas (tabs):

- **Measurement:** Where you capture real-time frequency responses.
- **Analysis:** Dedicated to detailed examination of your measurements, including the "Automated Diagnostics Engine" and L/R comparisons.
- **History (Vault):** A database of all your past measurements. You can load, compare, and export older traces here.
- **Profile:** Set up specific profiles for different IEM models, including target curves and reference images.

## 2. Performing Measurements

In the **Measurement** tab, you perform acoustic measurements of your IEMs.

- **Multi-Sweep:** For greater accuracy, the software can emit several frequency sweeps (multi-sweep) consecutively and average the results. This minimizes background noise and interference.
- **Smoothing:** Raw acoustic data often contains small, inaudible spikes (comb filtering). Using the *Smoothing* function (e.g., 1/12 or 1/24 octave) averages the curve, making it better align with human hearing and visually easier to read.
- **Process:** Position the IEM in the measurement coupler, ensure a tight acoustic seal, and press Start (or `Space`). After completion, you can save the resulting trace.

## 3. Settings Slide-Out (Routing & Calibration)

On the side of the app, you will find the **Settings Slide-Out**.

- **Routing:** Define which audio inputs (measurement mic/coupler) and outputs (headphone out to IEM) are used.
- **Calibration:** Microphones are rarely 100% linear. Load a calibration file (`.cal` or `.txt`) to compensate for your microphone's specific deviations. The calibration is applied in real-time to all incoming measurements.

## 4. Automated Diagnostics Engine

The "Automated Diagnostics Engine" (in the Analysis tab) evaluates your measurement to detect hardware defects or user errors automatically. The acoustic thresholds are based on industry standards and psychoacoustic literature (e.g., IEC 711 standards).

### How the diagnostics work (and why they are strict):

*   **Relative Phase (Polarity Inversion):**
    The engine does *not* check if a single IEM has an "absolute" phase inversion. Absolute phase is often introduced by soundcards, cables, or intentional crossover designs (like in multi-BA IEMs), and is generally inaudible to the human ear.
    Instead, the engine checks for **relative phase**: Are the left and right channels wired *oppositely*? If they are out of phase with each other, a strict FAIL is triggered. A relative phase mismatch leads to massive bass cancellation and the collapse of the stereo image. (In this case, check if your 2-pin/MMCX cables are inserted correctly).

*   **Bass / Acoustic Seal Leak:**
    The engine compares the bass region (50 Hz) against the midrange (1 kHz).
    - **WARNING:** Triggered when the bass drops by at least -10 dB compared to 1 kHz. For a neutral in-ear monitor (e.g., Etymotic or Diffuse-Field tuning), a drop of -2 to -6 dB is completely normal. A drop of -10 dB or more strongly indicates that the IEM is not optimally sealed in the measurement tube (leakage).
    - **FAIL:** Triggered only at -18 dB or worse. Such an extreme, steep drop in the low frequencies behaves physically like a high-pass filter, proving a massive air leak (seal break) in the coupler or a completely dead dynamic driver.

*   **Highs / Wax Clog:**
    A common flaw in simple measurement systems is checking exactly *one* specific frequency (e.g., 5 kHz). However, measurement tubes (IEC 711) have natural standing waves, often creating extremely narrow, deep dips (notches) precisely in this range.
    To avoid false alarms, our engine calculates the **average energy across the entire 4 kHz to 8 kHz band**. A true acoustic filter clogged with earwax physically acts like a low-pass filter, attenuating this entire frequency band broadly. The software will only trigger an alarm if this broadband average drops extremely low (-15 dB for a WARNING, -20 dB for a FAIL).

## 5. History Vault

The **History** tab acts as your secure vault. Every measurement you take can be saved and organized here. 
- You can overlay multiple historical traces to compare an IEM's wear over time or check consistency after cleaning.
- Easily export selected traces as CSV for sharing or external analysis.
- **Import CSV:** Click "Import CSV" to add an external measurement directly into the database.
- **Save as Target:** Export any history trace directly into your Reference Targets folder, immediately making it available as a Target curve across the app (similar to squiglink targets).
- **Rename Measurements:** Double click the "Notes" column to rename measurements in the history database directly.

## 6. Auto-Calibration (Auto-Generate from Reference)

If you don't own an expensive, calibrated IEC 711 measurement microphone (but use an affordable "fake" coupler), you can use the app to generate a custom calibration file!

Use the **"🪄 Auto-Generate from Reference"** button in the Calibration menu:

1. **Create your own measurement:** Measure a well-known, high-quality IEM using your own (fake) coupler and save this trace in the Measurement tab as a CSV.
2. **Click the button:** Open the Calibration menu (Settings Slide-Out) and click "🪄 Auto-Generate from Reference".
3. **Select files:**
   - *Step 1:* Select the CSV file of YOUR measurement (with the fake coupler).
   - *Step 2:* Select the professional CSV measurement (the "True" Reference) of the same IEM from the `reference_targets` folder.
4. **Magic!** The software interpolates both curves, matches their volume at 500Hz, and calculates the exact difference. It then generates an `Auto_Generated_Fake711_Cal.txt` file in the `calibrations` folder and applies it immediately. Your affordable microphone now measures just as linearly as the expensive reference setup!

## 7. Database Management

The Settings menu now has a **Database Management** section where you can Backup your entire SQLite database (`inearsnitch.db`) and Restore from previous backups. The system automatically creates a `.safety.bak` file when restoring to prevent accidental data loss.

## 8. Smart Searchable Dropdowns

The Target and History comboboxes across the application are fully searchable. You can type any part of the name (e.g., "v7") into the dropdown to quickly find matching entries (e.g., "Vision Ears v7").

## 9. Live RTA & IEC Guide (Insertion Depth)

At the bottom right of the main interface, you will find the **RTA (Real-Time Analyzer)** button. This mode plays "Pink Noise" and displays the measured frequency spectrum in real-time. It is used to position the IEM perfectly in the measurement coupler *before* starting the actual measurement sweep.

Directly below the RTA button is the **"IEC Guide"** checkbox (formerly "8k Helper").

### How does the IEC Guide work?
When the IEM is inserted into the measurement tube (IEC 711 coupler), a small cavity is formed between the IEM and the microphone. The air in this cavity physically resonates at a very specific frequency – the "Coupler Resonance". 

The IEC 711 standard was specifically designed in the 1980s so that this resonance simulates the human ear canal. For a comparable measurement (e.g., against databases from Crinacle or Super*Review), the IEM MUST be inserted to a depth where this physical resonance occurs exactly in the range of **7,000 Hz to 8,600 Hz** (classically ~8 kHz).

The *IEC Guide* displays a green target zone (7 - 8.6 kHz) and a crosshair that tracks the current resonance peak in real-time.
- Red Text ("Push Deeper"): Resonance is below 7 kHz -> Push the IEM further into the tube.
- Red Text ("Pull Out Slightly"): Resonance is above 8.6 kHz -> Pull the IEM out a tiny bit.
- Green Text ("Depth OK"): Perfect insertion depth achieved!

### Why always 8 kHz – even with different calibrations?
A common question is why the guide *always* aims for 8 kHz, even if completely different microphone calibration profiles are loaded.
The answer lies in **physics**: A calibration file (whether Dayton, Sonarworks, or "Fake 711") only corrects the internal flaws of the tiny microphone capsule itself (e.g., if the microphone naturally records slightly too quiet at 10kHz). 
However, the physical metal tube of the coupler remains exactly the same length. Therefore, a software calibration never shifts the physical 8 kHz air resonance. The guide will thus always show you the acoustically correct physical insertion depth, completely independent of the selected calibration file.

## 10. Health & Safety Disclaimer (EULA)

On the very first launch of InEar Snitch, a **Health & Safety Disclaimer** dialog is displayed. This dialog warns you about two critical risks:

- **Hearing damage:** **Never** wear IEMs in your ears while a measurement (sweep or stress test) is running! The signal levels produced during measurements can permanently damage your hearing.
- **Hardware damage:** Improper level settings can damage sensitive IEM drivers (especially Balanced Armature drivers).

You must click **"Accept"** to proceed and use the app. Clicking **"Decline"** will close the app immediately. This dialog appears only once – your acceptance is stored permanently in the app settings.

## 11. Output Level Calibration

The app includes an automatic level calibration feature that determines the optimal **output level** (output amplitude) for your specific hardware configuration. You can find this function under **Settings > "Start Auto-Calibration"**.

### Calibration Process:
1. The app plays a series of ascending test tones (starting at a low level).
2. It analyzes the recorded level and automatically finds the optimal sweep amplitude.
3. **Target recording peak:** -15 dBFS – this ensures a safe headroom margin from clipping while maintaining a sufficient signal-to-noise ratio.

### Possible Warnings:
- **Recording peak too low (< -30 dBFS):** The recorded signal is too quiet despite maximum sweep amplitude. **Solution:** Increase the system output level (OS volume) and re-run the calibration.
- **Stress test limited:** If the stress test cannot be output louder than the normal sweep (both at the amplitude cap), a warning appears indicating that Rub & Buzz detection may be unreliable.

> ⚠️ **Important terminology note:** This calibration adjusts the **output level** (output amplitude / sweep amplitude) – NOT the gain! Gain refers to the microphone preamplification on your audio interface's input and is not modified by the app.

## 12. Preflight Level Check

Before **every** measurement – both normal sweeps and stress tests – InEar Snitch automatically performs a quick **Preflight Level Check**.

### Process:
1. The app plays a short test tone (100 ms).
2. The recorded level is compared against the stored **calibration reference value**.

### Detected Situations:

- **Level deviation > 4 dB:** If the level has shifted by more than 4 dB since the last calibration (e.g., because someone changed the system output level), a pop-up appears:
  > *"Level shifted by X dB since calibration. Do you want to continue anyway?"*
  
  You can proceed with **Yes** or cancel with **No** and re-calibrate first.

- **Clipping detected (> -1 dBFS):** The input signal is clipping – the level needs to be reduced.
- **No signal detected (< -55 dBFS):** No usable signal is being received – check your cabling and routing.

## 13. DSP/EQ Safety Cap

When the built-in **DSP Engine** (integrated EQ) is active, frequency boosts can amplify the output signal beyond the original sweep amplitude.

To prevent damage to sensitive drivers, InEar Snitch **automatically applies a safety limiter after EQ processing**. This ensures that EQ boosts can **never** exceed the maximum sweep amplitude.

This is especially important for sensitive **Balanced Armature drivers**, which can be permanently damaged by overdrive. The Safety Cap operates transparently in the background – no configuration is required.

## 14. Troubleshooting Guide: Abnormal Measurements

> **CORE MESSAGE:** When in doubt: take the IEM out, reseat it, and measure again. Most issues are seal problems, not hardware defects.

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **Clipping / Overdrive** (Frequency response looks cut off, plateau at high dB) | Output Level set too high | Re-run level calibration, target -15 dBFS |
| **Bass Drop / No Bass** (Graph drops steeply below 200 Hz) | 1. Poor seal in coupler, 2. Weak headphone preamp, 3. Normal BA-driver roll-off | Reseat IEM, check Blu-Tack, use a better headphone output if needed |
| **Phase Inverted** (Diagnostics report "L/R OUT OF PHASE") | Cheap USB sound cards invert the phase | Check 2-pin cable orientation. If both sides are inverted = no problem |
| **High Distortion (THD)** (THD graph shows >5% in mid-range) | 1. Background noise (HVAC, footsteps), 2. Interface clipping internally | Measure in a quiet environment, check Level |
| **Signal Too Quiet** (Graph < -50 dBFS, diagnostics fail) | Mic Gain on the interface is too low | Turn up Gain on the mic preamp (not the Output Level!) |
| **Inconsistent Results** (Every measurement looks different) | Coupler position varies, IEM slips | Use 5x Sweep (Averaging), secure IEM with Blu-Tack |
| **Treble Peaks at 8 kHz** (Sharp peak at 8 kHz) | IEC-711 coupler resonance (normal!) | This is normal, not a defect. Use IEC Guide (Depth Tool) to calibrate insertion depth |

## 15. Additional Troubleshooting & Best Practices (CRITICAL)

### 1. My frequency response is a perfectly flat line!
If you see a nearly perfectly flat line after running a sweep, this is 99% of the time caused by **Operating System Audio Filters** (AGC / Auto-Gain / Voice Isolation):
- **macOS:** Click the yellow microphone icon in the Control Center (top right) and change the microphone mode to **"Standard"** (NOT "Voice Isolation").
- **Windows:** In your sound settings, disable all "Audio Enhancements" for your measurement microphone.
These dynamic range compressors try to suppress the extremely loud measurement sweep in real time. This aggressively flattens the recorded audio amplitude, resulting in a completely false, flat-line graph after deconvolution.

### 2. Warning: "Signal too quiet" despite high volume
InEar Snitch deliberately outputs the measurement sweep at a very low digital volume (-20 dBFS) to prevent your microphone from clipping. An In-Ear Monitor inside a sealed silicone coupler generates well over 115 dB SPL! Outputting a full-scale sweep (0 dBFS) would instantly clip the ADC (Analog-to-Digital Converter) of your sound card, which *also* results in a perfectly flat and invalid curve. If the app warns you that the signal is too quiet, you should increase the physical input gain on your microphone interface, not your headphone volume.
