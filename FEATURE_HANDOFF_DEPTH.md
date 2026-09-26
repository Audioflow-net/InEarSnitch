# FEATURE HANDOFF: Smart Depth Matching (History Resonance Target)

## 1. Goal
Provide the user with a visual guide during the "Depth" (Live RTA) phase that shows the insertion depth (resonance frequency) of the *last* measurement for the currently selected IEM profile, ensuring perfect reproducibility.

## 2. Database Migration (`database.py`)
- We need a new column to store the resonance frequency.
- **Action:** Add `resonance_hz REAL` to the `Measurements` table creation schema.
- **Migration:** Add a try/except block on startup to `ALTER TABLE Measurements ADD COLUMN resonance_hz REAL` for existing databases.

## 3. Data Extraction (`main.py` -> `on_measurement_finished`)
- After a successful measurement sweep, before calling `self.db.add_measurement(...)`, we need to find the primary Helmholtz resonance.
- **Logic:** Search the frequency array (`f`) between `6000 Hz` and `10000 Hz`. Find the index of the maximum magnitude (`mag`).
- Extract this frequency: `resonance_hz = f[peak_idx]`.
- Pass this to the database insert function.

## 4. UI Implementation: Live RTA (`main.py` & `analysis_ui.py`)
- When `toggle_live_seal(True)` is called, fetch the `resonance_hz` of the LAST measurement for `self.current_iem_id` from the database.
- **The Graph Marker:**
  - If a historical resonance exists, add a vertical dashed line (`pg.InfiniteLine`) to the live RTA plot widget at that exact frequency.
  - Color: Orange/Amber (distinct from the green/red RTA line).
- **The Text Overlay (`rta_big_lbl`):**
  - Keep the current logic for coloring the main text (Green ONLY if in the absolute physical ideal range of 6500-8600 Hz, with 8000 being the text target).
  - Append a second line of text (smaller, orange font): `<br><span style='font-size: 24px; color: #f59e0b;'>📍 Letzte Messung: {historical_hz} Hz</span>`.

## 5. History UI (`main.py` / `profile_ui.py`)
- In the History list/tab, when displaying old measurements, display the `resonance_hz` (if available) so the user can document it.

## ⚠️ SAFETY CONSTRAINTS (CODE FREEZE)
- Do **NOT** modify `audio_engine.py`.
- Do **NOT** modify the actual test signal generation or measurement threads (`MeasurementWorker`). 
- All data extraction must happen purely on the *results* passed back to `on_measurement_finished`.
