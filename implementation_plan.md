# Single-Ear Measurement & Gain Tracking Refactor

The user always measures IEMs one at a time using a single microphone coupler, rather than a dual-mic setup. We need to refactor the measurement pipeline to support sequential L/R captures, and add a text field for preamp gain tracking.

## Proposed Changes

### 1. `audio_engine.py`
#### [MODIFY] `audio_engine.py`
- Modify `measure()` to accept a `target_channel` parameter ('L' or 'R').
- Create a stereo output array but only put the sweep on the `target_channel` (0 for L, 1 for R).
- Record only 1 input channel (`channels=1`) from the measurement mic.
- Return a single set of `(freqs, mag, phase)` instead of stereo arrays.

### 2. `main.py`
#### [MODIFY] `main.py`
- **UI Updates**:
  - Replace `cb_chan` with a `QComboBox` or two `QPushButton` toggles: "Measure LEFT" and "Measure RIGHT".
  - Add a `QLineEdit` for "Mic Gain (dB)" to the toolbar.
- **State Management**:
  - Add `self.temp_mag_l`, `self.temp_mag_r`, `self.temp_phase_l`, `self.temp_phase_r` to hold the sequential captures in memory before saving.
  - When "Capture" is clicked, run the measurement for the selected channel and update the temporary variables.
  - Update the plot to show whatever temporary data exists.
  - Run `Analyzer.lr_imbalance_check()` only when BOTH `temp_mag_l` and `temp_mag_r` have been populated.
  - Save the combined data to the database when a "Save Measurement" button is clicked, or auto-save/update the DB row progressively.

### 3. `database.py`
#### [MODIFY] `database.py`
- Add a `gain_db` text/float column to the `Measurements` table to store the preamp gain value.
- Update `save_measurement()` to handle partial saves (e.g., saving just L, then updating the row when R is captured) or require both.

## Verification Plan
- Run the UI and click "Measure LEFT". Verify only the blue line plots.
- Click "Measure RIGHT". Verify the orange line plots and the imbalance check runs.
- Verify gain is saved to the database.
