# M2 Adversarial Challenge Report: Database Schema, Migrations & Query APIs

**Author**: M2 Empirical Challenger 2 (Archetype: empirical-challenger, Roles: critic, specialist)  
**Date**: 2026-09-22  
**Target Module**: `/Users/ben/Desktop/InEarSnitch/database.py`  
**Verdict**: **APPROVE**

---

## 1. Observation

### Implementation Details in `database.py`
- **Schema & Migration** (`_init_db`):
  - Creates table `TipProfiles` with columns `(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, material TEXT, color_hex TEXT, icon_char TEXT, is_default INTEGER DEFAULT 0)`.
  - Deterministically inserts seed tips with explicit IDs:
    - `id=1`: "Unbekannt" (`#6b7280`, `?`, `is_default=0`)
    - `id=2`: "Kein Aufsatz" (`#94a3b8`, `○`, `is_default=0`)
    - `id=3`: "Standard Foam" (`#f59e0b`, `●`, `is_default=0`)
    - `id=4`: "ProKit V1" (`#3b82f6`, `◆`, `is_default=0`)
    - `id=5`: "ProKit V2" (`#10b981`, `★`, `is_default=1`)
  - Uses `INSERT OR IGNORE INTO TipProfiles` to preserve pre-existing entries and guarantee idempotency.
  - Adds `tip_id INTEGER DEFAULT 1 REFERENCES TipProfiles(id)` to `Measurements` via `ALTER TABLE ... ADD COLUMN` inside `try/except sqlite3.OperationalError`.
  - Executes legacy backfill: `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL`.
- **Query & DSP APIs**:
  - `get_all_tips(include_unknown=True)`: Queries `TipProfiles ORDER BY id ASC`; when `include_unknown=False`, filters `WHERE id != 1`.
  - `get_last_used_tip(iem_id)`: Queries `Measurements WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1 ORDER BY timestamp DESC, id DESC LIMIT 1`. Returns `int | None`.
  - `save_measurement(...)`: Extended with `tip_id=1` parameter; coerces `None` to `1`.
  - `get_reproducibility_scores(iem_id, tip_id)`: Interpolates curves to `np.linspace(20.0, 8000.0, 800)`, calculates mean std dev in dB separately for Left and Right channels; returns `None` if count < 5; sets `is_preliminary = bool(count < 10)`.
  - `get_seal_history(iem_id, tip_id)`: Extracts 40 Hz (`35-45 Hz`) and 500 Hz (`450-550 Hz`) from stored BLOBs, calculates `delta = val_40 - val_500`, classifies `seal_ok = bool(delta_db >= -11.8)`.
  - `get_tip_target_peak(iem_id, tip_id)`: Finds max peak frequency in 6–10 kHz window for Left and Right, computes median across measurements.

### Test Execution Observations
1. **Smoke Test Baseline**:
   - Command: `python3 smoke_test.py`
   - Result: `✅ ALL 19 CHECKS PASSED`
2. **Adversarial Database Test Suite** (`tests/test_prokit_adversarial_db.py`):
   - Command: `python3 -m pytest -v tests/test_prokit_adversarial_db.py`
   - Result: `26 passed in 0.71s` (100% pass)
3. **Adversarial DSP Test Suite** (`tests/test_adversarial_dsp.py`):
   - Command: `python3 -m pytest -v tests/test_adversarial_dsp.py`
   - Result: `20 passed in 0.64s` (100% pass)
4. **Safety Verification**:
   - `inearsnitch.db` was untouched. All tests operated on ephemeral tempfile/tmp_path databases.

---

## 2. Logic Chain

1. **Repeated Initialization & Idempotency**:
   - Running `_init_db()` 100 consecutive times on the same database produced exactly 5 rows in `TipProfiles`, exactly one row with `id=1`, and exactly one row with `is_default=1`.
   - Running 20 concurrent threads calling `DatabaseManager(db_path)` resulted in zero exceptions and `PRAGMA integrity_check` returned `ok`.
   - *Inference*: Initialization is strictly idempotent and safe against repeated or concurrent instantiation.

2. **Large Legacy Migration Stress**:
   - Synthetically constructed a legacy database with 1,000 legacy records missing `tip_id`.
   - Migration took <0.05 seconds, backfilled all 1,000 rows to `tip_id = 1`, leaving zero NULLs.
   - Tested 5,000 records: 100% backfilled to `tip_id = 1` with zero data corruption.
   - Tested mixed database with pre-existing known tips (`tip_id = 4, 5`) alongside NULLs: known tips were preserved and only NULLs were backfilled to 1.
   - *Inference*: Legacy migration scales efficiently to thousands of records and does not overwrite existing known tip assignments.

3. **Pre-Existing Custom TipProfiles Preservation**:
   - Injected a custom tip into `TipProfiles` at `id=1` ("Custom SpinFit") prior to `_init_db()`.
   - Because `INSERT OR IGNORE` was used, `id=1` was preserved with its custom name and attributes. Missing seed tips (`id=2..5`) were cleanly appended.
   - *Inference*: Existing custom databases are protected against row overwrites.

4. **`get_last_used_tip` Query Logic**:
   - If an IEM has only `tip_id = 1` measurements, `get_last_used_tip` returns `None` (R2 requirement satisfied).
   - If measurements interleave unknown and known tips (e.g. Tip 4 → Tip 1 → Tip 5 → Tip 1), it correctly returns `5`.
   - If multiple measurements share the exact same second timestamp (`CURRENT_TIMESTAMP` resolution), `ORDER BY timestamp DESC, id DESC` breaks ties by auto-increment ID deterministically.
   - If `iem_id` is `None`, `0`, negative, or nonexistent, it returns `None` without crashing.
   - Different IEM models maintain complete measurement isolation.

5. **`save_measurement` Robustness**:
   - Passing `tip_id = None` defaults to `1` ("Unbekannt").
   - Passing all array vectors as `None` stores empty byte strings `b''` without throwing `AttributeError`.
   - Large arrays (100,000 bins) save and reload with full 64-bit precision.
   - SQLite type coercion cleanly accepts numeric floats (`4.0`) and numeric strings (`"5"`).

6. **DSP APIs Adversarial Robustness**:
   - Truncated, odd-byte, or corrupted BLOBs are caught by `try/except` and skipped without aborting calculations.
   - Ultrasonic or out-of-band frequencies (>8000 Hz only) are excluded from the reproducibility grid.
   - Exact boundary test at -11.8 dB: -11.79 dB → OK, -11.80 dB → OK, -11.81 dB → LEAK.
   - Target peak in 6-10 kHz handles flat spectrums and missing frequency bands gracefully.

---

## 3. Adversarial Challenges & Risk Assessment

### Challenge Summary
**Overall Risk Assessment**: **LOW**

### Challenges

#### Challenge 1: Unenforced SQLite Foreign Keys and Orphaned `tip_id`
- **Assumption Challenged**: `Measurements.tip_id` references `TipProfiles(id)` and callers only provide valid tip IDs.
- **Attack Scenario**: Calling `save_measurement(..., tip_id=999)` succeeds because SQLite disables foreign keys by default (`PRAGMA foreign_keys = ON` is not enabled). Subsequently, `get_last_used_tip` queries `Measurements` without joining `TipProfiles`, returning `999`.
- **Blast Radius**: If `999` is returned to the UI ComboBox, `cb_tip.findData(999)` returns `-1`, resulting in the previous valid tip selection not being suggested.
- **Mitigation / Defense**: In `history_ui.py`, `LEFT JOIN TipProfiles` with `COALESCE(t.name, 'Unbekannt')` already handles unknown tip IDs gracefully. For `get_last_used_tip`, adding `JOIN TipProfiles t ON Measurements.tip_id = t.id` in a future refactor would make it completely immune to orphaned tip IDs. Current risk is LOW since UI only allows selection from the catalog (no freetext).

#### Challenge 2: Non-Overlapping Frequency Grids in `np.interp`
- **Assumption Challenged**: Frequency responses always cover the 20 Hz – 8000 Hz band.
- **Attack Scenario**: If a sweep starts at 100 Hz (e.g. partial sweep), `np.interp` flat-lines the 20–100 Hz segment at `mag[0]`. If compared against a full sweep starting at 20 Hz, the flat-line extrapolation introduces artificial variance in the 20–100 Hz band.
- **Blast Radius**: Slight deviation in reproducibility score for partial sweeps.
- **Mitigation / Defense**: Coupler sweeps in InEarSnitch standard protocol always cover 20 Hz – 20+ kHz. The minimum frequency length check (`len(f_sub) >= 2` and `len(f) >= 10`) prevents index crashes.

---

## 4. Caveats

1. **Pre-existing id=1 naming**: If an external database already had a custom tip with `id=1`, `_init_db()` preserves it, but legacy measurements will be assigned to that tip since the backfill query is `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL`. In production InEarSnitch environments, `TipProfiles` is created for the first time by this migration, so `id=1` is guaranteed to be "Unbekannt".
2. **`main.py` UI Integration**: End-to-end tests for `main.py` UI widgets (`cb_prokit_tip`, `InEarSnitchApp`) are owned by M3/E2E track and are not part of `database.py`.

---

## 5. Conclusion & Verdict

**Verdict**: **APPROVE**

All required M2 scenarios were thoroughly tested and verified:
1. Repeated DatabaseManager initialization is strictly idempotent (100x serial and 20x concurrent threads verified).
2. Large legacy migrations (1,000 and 5,000 records) execute rapidly (<0.05s) with 100% backfill accuracy.
3. Pre-existing custom TipProfiles preserve `id=1` without being overwritten.
4. `get_last_used_tip` correctly handles unknown tips, interleaving known/unknown measurements, sub-second ties, deleted/invalid IEMs, and multi-IEM isolation.
5. `save_measurement` gracefully handles `tip_id=None`, non-existent IDs, negative IDs, None arrays, and 100k-bin arrays.
6. All 19 smoke tests pass, and all 46 adversarial tests across `test_prokit_adversarial_db.py` (26 tests) and `test_adversarial_dsp.py` (20 tests) pass with 100% success.

---

## 6. Verification Method

To independently reproduce and verify all adversarial results, run:

```bash
cd /Users/ben/Desktop/InEarSnitch

# 1. Verify smoke test
python3 smoke_test.py

# 2. Run M2 Database Adversarial Suite (26 tests)
python3 -m pytest -v tests/test_prokit_adversarial_db.py

# 3. Run M2 DSP Adversarial Suite (20 tests)
python3 -m pytest -v tests/test_adversarial_dsp.py
```
