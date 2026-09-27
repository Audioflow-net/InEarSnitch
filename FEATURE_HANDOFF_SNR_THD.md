# FEATURE HANDOFF: Smart SNR THD Masking

## 1. Goal
Prevent false-positive THD (Distortion) alarms when measuring in loud environments (like EDM stages). If loud background noise corrupts the sweep, the THD diagnostic cards should be disabled to prevent user panic, while preserving the raw Frequency Response data.

## 2. DSP Theory (Farina Log Sweep SNR)
Because Farina sweeps distribute uncorrelated background noise across the entire resulting Impulse Response (IR), we can easily determine if a sweep was corrupted by loud noise by checking the "tail" of the IR. An IEM decays completely within 5ms. Any energy found 50ms *after* the main impulse is 100% environmental noise that occurred *during* the sweep.

## 3. Implementation Plan

### A. The Math (Helper Function)
Add this helper function in `main.py` (or a utility file) to extract SNR directly from the unshifted IR:

```python
def calculate_measurement_snr(ir_data, sample_rate):
    import numpy as np
    peak_idx = np.argmax(np.abs(ir_data))
    
    # Signal window: Peak + 10ms
    signal_len = int(0.010 * sample_rate)
    signal_window = ir_data[peak_idx : peak_idx + signal_len]
    
    # Noise window: Peak + 50ms to 150ms
    noise_start = peak_idx + int(0.050 * sample_rate)
    noise_end = peak_idx + int(0.150 * sample_rate)
    
    if noise_end > len(ir_data):
        return 100.0 # Fallback if IR is too short
        
    noise_window = ir_data[noise_start : noise_end]
    
    rms_signal = np.sqrt(np.mean(signal_window**2))
    rms_noise = np.sqrt(np.mean(noise_window**2))
    rms_noise = max(rms_noise, 1e-12)
    
    snr_db = 20 * np.log10(rms_signal / rms_noise)
    return snr_db
```

### B. Database Migration (`database.py`)
1. Add two new columns to `Measurements`:
   - `snr_l REAL`
   - `snr_r REAL`
2. Update the `ALTER TABLE` loop to include these safely.
3. Update `save_measurement()` and the `INSERT INTO` query to accept and save these parameters.
4. Update the tuple unpacking in `load_history()` in `history_ui.py` so the app doesn't crash when reading old rows.

### C. Data Extraction (`main.py`)
In `on_measurement_finished`, run the `calculate_measurement_snr(ir, 48000)` function for the measured channel.
Save the result to `self.temp_snr_l` or `self.temp_snr_r`.
Pass these temporary variables to `self.db.save_measurement()` when the user saves.

### D. UX Muting (`analysis.py` / `analysis_ui.py`)
When rendering the diagnostic cards for THD and CSD:
Check the `snr` value (either from live temp vars or loaded DB history).
If `snr < 40.0 dB`:
1. Hide all normal THD evaluation cards.
2. Inject a single, gray warning card:
   **Title:** ⚠️ THD / CSD Analysis Disabled
   **Body:** `Measurement corrupted by environmental noise (SNR: {snr:.1f} dB). Frequency Response is still valid, but distortion metrics are unreliable.`
3. *(Optional)* Apply a 50% opacity mask or dashed line style to the THD plot line.

## ⚠️ SAFETY CONSTRAINTS (CODE FREEZE)
- Do **NOT** modify `audio_engine.py` or the `MeasurementWorker`!
- All logic must be handled post-sweep in `main.py` or `analysis.py`.
- Run `python3 smoke_test.py` before finalizing any UI logic.
