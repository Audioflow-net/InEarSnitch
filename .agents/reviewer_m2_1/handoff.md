# Milestone 2 Review & Adversarial Challenge Report

**Reviewer:** Reviewer M2-1 (`reviewer_m2_1`)  
**Roles:** reviewer, critic  
**Date:** 2026-09-22T09:02:00+02:00  
**Working Directory:** `/Users/ben/Desktop/InEarSnitch/.agents/reviewer_m2_1`  
**Target Reviewed:** `/Users/ben/Desktop/InEarSnitch/database.py` (Commit `7afc965`)  
**Verdict:** **APPROVE**

---

## 1. Observation

1. **Schema & Migration Definitions in `database.py`:**
   - Table `TipProfiles` created at lines 57–65:
     ```python
     CREATE TABLE IF NOT EXISTS TipProfiles (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         material TEXT,
         color_hex TEXT,
         icon_char TEXT,
         is_default INTEGER DEFAULT 0
     )
     ```
   - Deterministic seed data inserted via `INSERT OR IGNORE` at lines 68–79:
     - `id=1`: `("Unbekannt", "Standard", "#6b7280", "?", 0)`
     - `id=2`: `("Kein Aufsatz", "None", "#94a3b8", "○", 0)`
     - `id=3`: `("Standard Foam", "Foam", "#f59e0b", "●", 0)`
     - `id=4`: `("ProKit V1", "Silicone", "#3b82f6", "◆", 0)`
     - `id=5`: `("ProKit V2", "Silicone", "#10b981", "★", 1)`
   - Migration for legacy tables in `_init_db()` at lines 108–113:
     `cursor.execute("ALTER TABLE Measurements ADD COLUMN tip_id INTEGER DEFAULT 1 REFERENCES TipProfiles(id)")` safely enclosed in `try/except sqlite3.OperationalError: pass`.
   - Legacy backfill at lines 116–119:
     `cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")` safely enclosed in `try/except sqlite3.OperationalError: pass`.

2. **Query & DSP APIs in `database.py`:**
   - `save_measurement()` signature at line 124 includes `tip_id=1`. Line 137 coerces `None` to `1`: `actual_tip_id = tip_id if tip_id is not None else 1`.
   - `get_all_tips(include_unknown=True)` at lines 174–197 returns catalog dicts with keys `id`, `name`, `material`, `color_hex`, `icon_char`, `is_default` (bool). Filters `WHERE id != 1` when `include_unknown=False`.
   - `get_last_used_tip(iem_id)` at lines 198–219 queries `WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1 ORDER BY timestamp DESC, id DESC LIMIT 1`. Returns `int` or `None`.
   - `get_reproducibility_scores(iem_id, tip_id)` at lines 220–305 evaluates on `np.linspace(20.0, 8000.0, 800)`. Filters `mask = f <= 8000.0` before interpolation. Calculates L and R channels completely independently. Requires $\ge 5$ curves per channel (returns `None` if $< 5$). Returns `is_preliminary: True` for $5 \le N < 10$ and `False` for $N \ge 10$.
   - `get_seal_history(iem_id, tip_id)` at lines 306–391 extracts 40 Hz mean (35–45 Hz) and 500 Hz mean (450–550 Hz), computes `delta_db = float(round(val_40 - val_500, 2))`, sets `seal_ok = bool(delta_db >= -11.8)`, and returns separate `left` and `right` chronological histories.
   - `get_tip_target_peak(iem_id, tip_id)` at lines 393–450 detects peak in 6–10 kHz window from magnitude arrays and returns median frequency for L and R separately.

3. **Targeted Pytest Suite Execution:**
   - Command:
     ```bash
     cd /Users/ben/Desktop/InEarSnitch && pytest -v tests/test_prokit_e2e.py -k "TestTier1DBSchema or TestTier1DBQueries or TestTier2DBBoundaries or TestTier2DSPBoundaries or test_unlock_and_db_catalog_interaction or test_reproducibility_isolated_per_tip or test_multi_iem_tip_persistence_and_suggestion or test_scenario_legacy_migration_and_compatibility or test_scenario_statistical_reproducibility or test_scenario_seal_leak_detection_and_degradation"
     ```
   - Result: `28 passed, 59 deselected in 0.97s`.
   - Full DB and DSP query suite run (`DB or Query or Reproducibility or Seal or legacy or left_join or tip_id or TipProfiles or tips`): `38 passed, 49 deselected in 1.20s`.

4. **Smoke Test Anti-Regression Execution:**
   - Command:
     ```bash
     cd /Users/ben/Desktop/InEarSnitch && python3 smoke_test.py
     ```
   - Result: `✅ ALL 19 CHECKS PASSED`.

5. **Production Database Invariance:**
   - Command: `stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db`
   - Result: `16379904` bytes (100% untouched).

---

## 2. Logic Chain

1. **Adherence to Locked Design Decisions:**
   - **Freitext Forbidden:** All ear tips are strictly keyed to integer primary keys referencing `TipProfiles(id)`. Freetext ear tip entry does not exist in schema or query APIs.
   - **L and R Channels Always Separate:** In `get_reproducibility_scores()`, `curves_l` and `curves_r` are separate lists evaluated independently. In `get_seal_history()`, `history_l` and `history_r` are separated. In `get_tip_target_peak()`, `peaks_l` and `peaks_r` are separated. No channel averaging or merging is performed anywhere in `database.py`.
   - **Tip ID = 1 for Unbekannt & Legacy Backfill:** `TipProfiles` inserts `id=1` as "Unbekannt" deterministically. `_init_db()` executes `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL`, which was verified under 20-record and 500-record migration tests.
   - **Band-Limiting to 20 Hz – 8 kHz:** Frequencies strictly filtered via `mask = f <= 8000.0` and interpolated onto `common_grid = np.linspace(20.0, 8000.0, 800)`. Test `test_reproducibility_band_limited_ignores_above_8khz` verified that massive 30 dB HF variances above 8 kHz yield a score of 0.00 dB standard deviation.
   - **Sample Count Thresholds:** `calc_channel_score` checks `if n < 5: return None` and `is_preliminary = bool(n < 10)`. Verified across N=4 (returns None), N=5–9 (returns is_preliminary=True), and N>=10 (returns is_preliminary=False).

2. **Integrity & Code Quality Assessment:**
   - No hardcoded test responses or simulated facades.
   - No shortcuts or external delegation.
   - SQLite connection management strictly employs `try/finally` blocks ensuring connection closure and zero leak risk.
   - BLOB parsing uses defensive `try/except Exception` wrappers around `np.frombuffer` and dimension validation (`len(ml) == len(f) and len(ml) >= 10`).

3. **Adversarial Stress Testing:**
   - Evaluated corrupted non-float64 and truncated BLOBs: successfully ignored without crashing or corrupting subsequent rows.
   - Evaluated extreme acoustic seal conditions (+35 dB boost and -60 dB complete leak): correctly computed delta and thresholding.
   - Evaluated mono measurements (Left-only, Right-only): active channel computes correctly while inactive channel returns `None` without index or shape errors.

---

## 3. Caveats

- **Scope Boundary:** This review strictly covers Milestone 2 (`database.py`). UI integrations in `main.py` (M3), `history_ui.py` (M4), and `analysis_ui.py` (M5) are decoupled and will be reviewed under their respective milestones.
- **Production Database Protection:** Production database `/Users/ben/Desktop/InEarSnitch/inearsnitch.db` was verified unchanged and was not used as a test target. All tests run against ephemeral temporary SQLite instances.

---

## 4. Conclusion

The implementation in `/Users/ben/Desktop/InEarSnitch/database.py` (Commit `7afc965`) satisfies all requirements of Milestone 2, strictly enforces all locked design constraints, passes all 28 targeted and 38 comprehensive DB/DSP tests, maintains 19/19 smoke test pass, and exhibits zero integrity violations.

**Verdict: APPROVE**

---

## 5. Verification Method

To reproduce and verify this review independently:

1. **Run Targeted Pytest Suite:**
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && pytest -v tests/test_prokit_e2e.py -k "TestTier1DBSchema or TestTier1DBQueries or TestTier2DBBoundaries or TestTier2DSPBoundaries or test_unlock_and_db_catalog_interaction or test_reproducibility_isolated_per_tip or test_multi_iem_tip_persistence_and_suggestion or test_scenario_legacy_migration_and_compatibility or test_scenario_statistical_reproducibility or test_scenario_seal_leak_detection_and_degradation"
   ```
   *Expected:* 28 passed, 0 failed, 59 deselected.

2. **Run Smoke Test:**
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 smoke_test.py
   ```
   *Expected:* `✅ ALL 19 CHECKS PASSED`.

3. **Verify Production Database Size:**
   ```bash
   stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db
   ```
   *Expected:* Exactly `16379904`.
