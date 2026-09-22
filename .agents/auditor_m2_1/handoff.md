# Forensic Integrity Audit Report: Milestone 2 (`database.py`)

**Work Product**: `/Users/ben/Desktop/InEarSnitch/database.py`  
**Integrity Mode**: Development (from `ORIGINAL_REQUEST.md`)  
**Verdict**: **CLEAN**

---

## 1. Observation

### 1.1 Source Code Inspection (`database.py`)
- **`_init_db` (lines 56–123)**:
  - Creates table `TipProfiles` with schema: `(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, material TEXT, color_hex TEXT, icon_char TEXT, is_default INTEGER DEFAULT 0)`.
  - Deterministically seeds default tips using `INSERT OR IGNORE`:
    ```python
    seed_tips = [
        (1, "Unbekannt", "Standard", "#6b7280", "?", 0),
        (2, "Kein Aufsatz", "None", "#94a3b8", "○", 0),
        (3, "Standard Foam", "Foam", "#f59e0b", "●", 0),
        (4, "ProKit V1", "Silicone", "#3b82f6", "◆", 0),
        (5, "ProKit V2", "Silicone", "#10b981", "★", 1),
    ]
    ```
  - Creates / alters `Measurements` to include `tip_id INTEGER DEFAULT 1 REFERENCES TipProfiles(id)`.
  - Executes legacy migration backfill:
    ```python
    cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")
    ```
- **`save_measurement` (lines 124–148)**:
  - Adds `tip_id=1` default parameter.
  - Handles `None` safely via `actual_tip_id = tip_id if tip_id is not None else 1`.
  - Inserts `actual_tip_id` directly into the database row.
- **`get_all_tips` (lines 174–197)**:
  - Queries `TipProfiles` table.
  - Supports `include_unknown=True` (all 5 tips ordered by `id ASC`) and `include_unknown=False` (`WHERE id != 1`).
  - Returns structured dicts containing `'id'`, `'name'`, `'material'`, `'color_hex'`, `'icon_char'`, `'is_default'`.
- **`get_last_used_tip` (lines 198–219)**:
  - Queries:
    ```sql
    SELECT tip_id 
    FROM Measurements 
    WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
    ORDER BY timestamp DESC, id DESC
    LIMIT 1
    ```
  - Correctly excludes `tip_id = 1` and `NULL`. Returns `None` if no valid prior tip exists.
- **`get_reproducibility_scores` (lines 220–305)**:
  - Queries raw BLOBs: `frequencies`, `magnitude_l`, `magnitude_r` for `iem_id` and `tip_id`.
  - Filters to 20–8000 Hz: `mask = f <= 8000.0` and interpolates to a common 800-bin grid: `np.interp(common_grid, f_sub, ml[mask])` where `common_grid = np.linspace(20.0, 8000.0, 800)`.
  - Computes Left and Right independently via `calc_channel_score(curves)`.
  - Enforces sample threshold: returns `None` if `n < 5`.
  - Calculates population standard deviation across sweeps: `std_per_bin = np.std(mat, axis=0, ddof=0)` and computes mean: `mean_std = float(round(float(np.mean(std_per_bin)), 2))`.
  - Sets `is_preliminary = bool(n < 10)`.
- **`get_seal_history` (lines 306–392)**:
  - Computes mean magnitude at 40 Hz: `mask_40 = (f >= 35.0) & (f <= 45.0)`, `val_40 = float(np.mean(ml[mask_40]))`.
  - Computes mean magnitude at 500 Hz: `mask_500 = (f >= 450.0) & (f <= 550.0)`, `val_500 = float(np.mean(ml[mask_500]))`.
  - Computes delta: `delta = val_40 - val_500`, rounded to 2 decimal places.
  - Evaluates seal threshold: `seal_ok = bool(delta_db >= -11.8)`, setting status `"OK"` if `seal_ok` else `"LEAK"`.
  - Processes Left and Right channels strictly independently.
- **`get_tip_target_peak` (lines 393–450)**:
  - Windows frequencies to 6000–10000 Hz: `mask = (f >= 6000.0) & (f <= 10000.0)`.
  - Locates peak index within window via `np.argmax(ml[mask])`.
  - Computes median across measurements: `round(float(np.median(peaks_l)), 1)`.
  - Left and Right channels computed separately.

### 1.2 Static Pattern & Anti-Cheat Analysis
- Grep search for `"test"`, `"mock"`, `"assert"` in `database.py`: 0 matches.
- Grep search for `==` comparisons in `database.py`: Only 6 occurrences, all checking array dimension consistency (`len(ml) == len(f)`).
- No conditional branching on test IDs, test names, or synthetic parameters.
- No canned numbers or pre-computed lookup tables.

### 1.3 Smoke Test & E2E Test Suite Results
- `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`:
  - Output: `✅ ALL 19 CHECKS PASSED`
- `pytest -v tests/test_prokit_e2e.py -k "DBSchema or DBQueries or DBBoundaries or DSPBoundaries or test_scenario_legacy_migration_and_compatibility or test_scenario_statistical_reproducibility or test_scenario_seal_leak_detection_and_degradation"`:
  - Result: `25 passed, 62 deselected in 0.92s` (100% pass rate).

### 1.4 Independent Mathematical & Robustness Verifications
- **Reproducibility Mathematical Exactness**:
  - Test input: 5 measurements with constant offsets $[0, 2, 4, 6, 8]$ dB for Left and $[0, 4, 8, 12, 16]$ dB for Right.
  - Theoretical population standard deviation: Left = $\sqrt{8} \approx 2.8284 \rightarrow 2.83$ dB, Right = $2\sqrt{8} \approx 5.6568 \rightarrow 5.66$ dB.
  - Observed output: `Left score: 2.83`, `Right score: 5.66`. Exact match to theoretical mathematics.
- **Seal Threshold and Status Verification**:
  - Tested: $\Delta = -5.0 \text{ dB} \rightarrow \text{OK}$; $\Delta = -20.0 \text{ dB} \rightarrow \text{LEAK}$; $\Delta = -11.8 \text{ dB} \rightarrow \text{OK}$; $\Delta = -11.9 \text{ dB} \rightarrow \text{LEAK}$.
  - Observed output: Exact match across all four boundary conditions.
- **Resonance Peak Extraction and Out-of-Band Noise Rejection**:
  - Injected artificial out-of-band peaks of $+999$ dB at 3000 Hz and 15000 Hz, with genuine in-band peaks at 7150 Hz / 7250 Hz (Left) and 8420 Hz / 8400 Hz (Right).
  - Observed output: `Left peak median: 7200.0`, `Right peak median: 8410.0`. Out-of-band signals were completely rejected; in-band medians were calculated accurately.
- **Corrupt / Truncated BLOB Resistance**:
  - Injected non-float64 byte buffers, truncated byte arrays, and mismatched frequency/magnitude lengths into `Measurements`.
  - Observed: All corrupt records safely skipped via `try...except Exception` blocks without raising unhandled exceptions or corrupting calculations.
- **Idempotency and Legacy Backfill**:
  - Initialized database on 500 legacy rows with `tip_id = NULL`. Verified all 500 updated to `tip_id = 1`. Multiple re-runs of `_init_db` preserve seed data and custom rows without duplicate key errors.

---

## 2. Logic Chain

1. **Premise**: An integrity violation occurs if code contains hardcoded test results, facade implementations returning constants without computation, test-specific bypass branches, or fabricated outputs.
2. **Observation 1.1 & 1.2**: Static analysis of all newly added methods in `database.py` reveals complete, genuine implementations utilizing SQLite SQL queries and NumPy array algorithms (`np.linspace`, `np.interp`, `np.std`, `np.mean`, `np.median`, `np.argmax`). Zero test-specific strings or bypass branches exist.
3. **Observation 1.3 & 1.4**: Runtime verification on isolated synthetic databases proves that:
   - `get_reproducibility_scores` executes true numerical interpolation and sample standard deviation calculations matching analytical ground truth to the second decimal place.
   - `get_seal_history` dynamically unpacks binary BLOBs, averages frequencies around 40 Hz and 500 Hz, and correctly classifies seal health against the $-11.8$ dB threshold.
   - `get_tip_target_peak` strictly restricts search to the 6–10 kHz window and extracts legitimate medians while rejecting massive out-of-band signals.
   - `get_last_used_tip` and `get_all_tips` conform to the specification and interface contracts without exception.
   - Corrupted BLOBs, mismatched arrays, and legacy migrations are handled robustly.
4. **Deduction**: The work product `/Users/ben/Desktop/InEarSnitch/database.py` is an authentic, robust, and mathematically sound implementation that fully satisfies all design requirements of Milestone 2 without taking shortcuts or implementing facade logic.

---

## 3. Caveats

- **GUI Integration**: This audit examined `database.py` specifically. Subsequent milestones (M3 UI Selector, M4 History Badges, M5 Diagnostics Display) rely on these APIs and will be audited in their respective phases.
- No other caveats.

---

## 4. Conclusion

- **Verdict**: **CLEAN**
- The implementation of Milestone 2 in `database.py` meets all technical, algorithmic, and architectural requirements of `ORIGINAL_REQUEST.md` and `PROJECT.md`.
- No integrity violations, facade implementations, or hardcoded shortcuts were detected.
- Recommendation: Proceed to Milestone 3 (UI Selector & Gate in `main.py`).

---

## 5. Verification Method

To independently reproduce and verify this audit:

1. **Smoke Test Verification**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   *Expected: All 19 checks pass.*

2. **Automated E2E / Database Test Suite**:
   ```bash
   pytest -v /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py -k "DBSchema or DBQueries or DBBoundaries or DSPBoundaries"
   ```
   *Expected: 22 passed.*

3. **Dynamic Numerical Reproducibility Verification**:
   ```bash
   python3 -c "
   import database, tempfile, os, numpy as np
   with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
       db = database.DatabaseManager(tf.name)
       f = np.linspace(20, 10000, 1000)
       for off in [0.0, 2.0, 4.0, 6.0, 8.0]:
           db.save_measurement(1, f, np.full_like(f, 80+off), np.full_like(f, 70+off*2), None, None, tip_id=4)
       res = db.get_reproducibility_scores(1, 4)
       assert res['left']['score'] == 2.83
       assert res['right']['score'] == 5.66
       print('VERIFIED')
   "
   ```
   *Expected: Prints `VERIFIED`.*
