# InEar Snitch: User Manual

Welcome to InEar Snitch, the professional software for measuring, analyzing, and diagnosing In-Ear Monitors (IEMs).
This manual explains the core features and guides you through performing accurate measurements.

👉 **New here?** Read the [What You Need – Hardware Guide](#hardware-guide) first to set up your audio equipment correctly!

## Keyboard Shortcuts

The following shortcuts will speed up your workflow:
- `Space`: Run Sweep (Start Measurement)
- `Ctrl+S` / `Cmd+S`: Save Trace
- `Backspace` / `Delete`: Clear Trace
- `Ctrl+1`, `Ctrl+2`, `Ctrl+3`, `Ctrl+4`: Switch between tabs (Profile, Measurement, Analysis, History)

<a name="hardware-guide"></a>
## What You Need – Hardware Guide

Before you can start measuring, you need the right hardware. InEar Snitch captures acoustic signals, so a correctly set up "measurement chain" is essential.

### 1. The Measurement Chain Explained

The measurement chain describes the path of the audio signal from the software to the IEM and back into the computer.

```text
[Computer] ──OUTPUT──▶ [IEM] ──▶ [IEC711 Coupler] ◀── [Measurement Mic] ──INPUT──▶ [Computer]
```

**How it works:**
- There is an **OUTPUT path** (sound to the IEM) and an **INPUT path** (microphone back to the computer).
- Both must work **SIMULTANEOUSLY** (Full-Duplex).
- InEar Snitch supports **SEPARATE** devices for input and output (e.g., MacBook headphone output + USB mic interface).

### 2. Audio System Requirements

**What your audio setup MUST be capable of:**
- Play and record at the same time (Full-Duplex).
- Appear in InEar Snitch as separate Input AND Output devices.
- Stable drivers (Core Audio on macOS, WASAPI on Windows).

**💡 macOS Specifics:**
- Input and Output **MAY** be different devices!
- Example: MacBook headphone output (Output) + USB Audio Interface (Input) → works perfectly!
- The app uses `sd.Stream()` internally instead of `sd.playrec()`, smoothly supporting separate devices.

**⚠️ Windows Specifics:**
- Input and Output **MUST** be set to the exact same sample rate (e.g., both 48000 Hz).
- Check this under: Control Panel → Sound → Recording/Playback → Properties → Advanced.
- If the sample rates do not match, the app will crash during measurements!

### 3. Three Setup Tiers (Price Ranges)

#### 💰 Budget Setup (~50-80€) – "I already have a Mac/PC"

**What you need:**
- **IEC711 Coupler with built-in microphone** (approx. 30€)
  - Search AliExpress: "IEC711 coupler microphone ear simulator"
  - Buy "Type 4" (without individual calibration) – the app has a built-in generic IEC711 correction file.
- **USB Audio Interface** (approx. 35-45€)
  - Behringer UM2 (approx. 35€) or Behringer UMC22 (approx. 45€)
  - Has its own headphone output (Output) + Jack/XLR input (Input).

**OR even cheaper:**
- **The 3€ Secret:** Tiny USB-C sound cards (e.g., on AliExpress) work wonderfully!
  - **IMPORTANT:** The dongle **MUST HAVE TWO separate jacks** (one for headphones, one for the mic).
- **IEC711 Coupler:** AliExpress Type 4 (approx. 30€).
- **In InEar Snitch:** Settings → Routing → Input = USB Sound Card, Output = USB Sound Card (or "Built-in Output" on Mac).
- **Total cost: starting around 35€!**

#### 💰💰 Recommended Setup (~100-200€)

- **IEC711 Coupler** with individual calibration file (approx. 60€)
- **USB Audio Interface:** Focusrite Scarlett Solo (approx. 100€) or MOTU M2 (approx. 180€)
  - Better preamps = less noise = cleaner measurements.
  - Stable, well-tested drivers for macOS and Windows.
- If you ALREADY own an audio interface (any brand: Focusrite, MOTU, RME, Universal Audio, PreSonus, Steinberg, Audient, Behringer...): Just buy the coupler!

#### 💰💰💰 Pro/Lab Setup (~400€+)

- **GRAS RA0045** or **Brüel & Kjær** Coupler (approx. 300-500€)
- **RME Babyface Pro FS** (approx. 500€) or **MOTU M2** (approx. 180€)
- Advantage: Lab quality, measurements are publishable and comparable with Crinacle/Headphones.com.

### 4. ⚠️ Is my setup working? The 60-Second Test

**Step-by-step guide:**
1. Open InEar Snitch → Settings (top right) → Routing Tab.
2. Select your interface as **Input** (the device with the microphone).
3. Select your interface or built-in output as **Output** (where the IEM is plugged in).
4. Click "Save".
5. Press **"RTA"** in the bottom bar.
6. Do you see a **lively, moving curve**? → Your microphone input is working ✅
7. Do you hear **Pink Noise** (a static sound) in the IEM? → Your output is working ✅
8. Stop RTA. Go to Settings → Calibration Tab → "Start Auto-Calibration".
9. The bars MUST **RISE** from left to right (quiet → loud).
10. If all bars are the same length (approx. -40 dBFS): Your setup is not receiving a real signal. Check your cables!

### 5. ❌ What does NOT work

| Setup | Problem |
|-------|---------|
| **Apple USB-C to 3.5mm Dongle** (and similar with only ONE jack) | They have a combined TRRS jack. They do not recognize pure measurement mics. TRRS splitter cables (Y-cables) do **not** work either! |
| **Bluetooth Headphones / AirPods** | Latency is way too high, no sweep possible. |
| **TWS Earbuds (wireless)** | Cannot be inserted into the coupler. |
| **Phone headphone jack** | Too weak, usually no full-duplex possible. |
| **Windows: Different Sample Rates** | App crashes! Input AND Output must be set to the same sample rate (e.g., 48000 Hz). |

### 6. Recommended Cables & Adapters

- **3.5mm to 6.3mm (1/4") Jack Adapter** (for interface headphone output → IEM, if needed)
- **TRS-to-TRRS Adapter** (only if you want to use the MacBook jack as an input at the same time – not recommended)
- ⚠️ **CRITICAL: XLR-to-Jack Adapter for Measurement Mics**
  If your audio interface only has XLR inputs and your IEC711 coupler has a 3.5mm jack, do not make the mistake of buying a simple, cheap adapter!
  - **The Problem:** Audio interfaces provide **48V Phantom Power** over XLR. However, the small microphone inside the coupler can only handle **3 to 5 Volts (Plug-in Power)**. If you send 48V directly into the mic, it will fry instantly.
  - **The Solution:** You absolutely need an adapter with a built-in voltage step-down ("Power Converter").
  - **How to read adapter specs:** Look for exact phrases in the product description like *"Converts 12-48V Phantom Power to 3-5V Plug-in Power"*. If this is not explicitly stated, the adapter will pass the full 48V through and destroy your mic!
  - **Recommendation:** Buy the **Rode VXLR+** (the "Plus" is crucial!) or the **Antlion Audio XLR Power Converter**.

### 7. 🔗 Useful Resources & Community

- **[REW Forum (Room EQ Wizard)](https://www.avnirvana.com/forums/rew-room-eq-wizard.4/)** → Community experiences with audio interfaces for measurements
- **[Head-Fi IEM Community](https://www.head-fi.org/)** → The largest IEM community in the world
- **[AudioScienceReview](https://www.audiosciencereview.com/)** → Objective reviews and measurements of audio hardware
- **[Squig.link](https://squig.link/)** → IEM frequency response comparison tool (to compare your own measurements)
- **[Crinacle IEM Rankings](https://crinacle.com/rankings/iems/)** → Reference for IEM evaluations based on measurements

**Search terms for hardware:**
- AliExpress: `IEC711 coupler microphone`, `IEC711 ear simulator`, `artificial ear IEC711`
- Amazon: `USB audio interface recording`, `Behringer UM2`, `Focusrite Scarlett Solo`
- Specifically for couplers with calibration: `IEC711 calibrated coupler with certificate`

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

## 9. Live Position Guide (RTA & Depth)

At the bottom right of the main interface, you will find the **RTA (Real-Time Analyzer)** and the **Depth** button. This mode plays "Pink Noise" and displays the measured frequency spectrum in real-time. It is used to position the IEM perfectly in the measurement coupler *before* starting the actual measurement sweep.

When you activate the **Depth** button, the app guides you in real-time through two critical physical properties of the measurement: **Air-Tightness (Seal)** and **Insertion Depth**.

### 1. Air-Tightness (Bass Seal / 40 Hz Line)
If the In-Ear Monitor does not form a 100% air-tight seal with the coupler, pressure escapes and the bass drops massively.
- **Green 40 Hz Line (Bass Seal OK):** The IEM is perfectly sealed.
- **Red 40 Hz Line (Bass Leak!):** Air is escaping. Push the IEM in straighter or use a different foam/silicone tip.

### 2. Insertion Depth (IEC Guide / 8 kHz Line)
When the IEM is inserted into the measurement tube (IEC 711 coupler), a small cavity is formed that resonates at a specific frequency. For standardized measurements, the IEM must be inserted exactly to a depth where this resonance lands in the green target zone between **7,000 Hz and 8,600 Hz**.
- **Yellow Text ("Push Deeper"):** Resonance is below 7 kHz -> Push the IEM further into the tube.
- **Yellow Text ("Pull Out Slightly"):** Resonance is above 8.6 kHz -> Pull the IEM out a tiny bit.
- **Green Text ("Depth OK"):** Perfect insertion depth achieved!

### Why always 8 kHz – even with different calibrations?
A common question is why the depth guide *always* aims for 8 kHz, even if different microphone calibration profiles are loaded.
The answer lies in **physics**: A calibration file only corrects internal frequency flaws of the microphone capsule. The physical metal tube of the coupler, however, remains exactly the same length. Therefore, a software calibration never shifts the physical air resonance. The guide will always show you the acoustically correct physical position, independent of the selected calibration file.

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

---

## 16. Liability Disclaimer & Hardware Safety (IMPORTANT!)

In addition to the software, the InEar Snitch system includes physical 3D-printed parts (TPU inserts) and cast silicone adapters. You must strictly observe the following hardware guidelines:

### Liability Disclaimer (Damage to In-Ears)
> **Use the adapters and the measurement rig at your own risk.**  
> Never use force when inserting In-Ear Monitors (especially sensitive Custom In-Ears made of acrylic). Be careful not to tilt or jam the sound nozzles. **We are not liable for any mechanical or cosmetic damage to your In-Ear Monitors.**

### Materials & Compatibility
- **Peli-Insert / Cradle:** The main housing is made of **TPU 95A** (Thermoplastic Polyurethane). It is robust, shock-absorbing, and chemically stable. However, protect it from extreme heat (e.g., in a car during mid-summer).
- **Measurement Adapters (Silicone):** The flexible adapters are made of **TFC Silicone Rubber Type 9 (Soft Putty Silicone Shore 25 1:1)**. This addition-curing (platinum) silicone does not outgas and contains no aggressive plasticizers or acetic acids. It is chemically neutral and will not attack the sensitive clear coat of your Custom In-Ears.

### Hardware Best Practices
- **This is not a medical device:** The entire kit is a measurement tool (jig) and must under no circumstances be inserted into the human ear canal.
- **Secure fit:** Before every measurement, ensure that the silicone adapter sits securely and flush on the TPU mount of the cradle so your IEM does not slip off when applying pressure.
- **Cleaning:** Do not use aggressive solvents like acetone or pure isopropanol on the TPU and silicone parts. A slightly damp cloth or glasses cleaning cloth is completely sufficient.
