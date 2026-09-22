# M2 E2E & Safety Verification Strategy Report

## 1. Observation

### 1.1 Existing Codebase & Safety Baseline
- **Production / Dev Database Presence**:
  - Command: `ls -la /Users/ben/Desktop/InEarSnitch/inearsnitch.db`
  - Output: `-rw-r--r--@ 1 ben staff 16379904 Sep 15 11:41 /Users/ben/Desktop/InEarSnitch/inearsnitch.db` (16.38 MB).
  - Inspection via SQLite read-only mode (`mode=ro`):
    - Tables: `['Musicians', 'sqlite_sequence', 'IEM_Models', 'Measurements', 'AppSettings', 'eq_presets']`.
    - `Measurements` row count: `9` records.
    - Columns: `['id', 'iem_id', 'timestamp', 'gain_db', 'frequencies', 'magnitude_l', 'magnitude_r', 'phase_l', 'phase_r', 'photo_path', 'notes', 'meas_name']`.
    - Column `tip_id` is currently **absent**.
    - Table `TipProfiles` is currently **absent**.
  - Documents Database: `~/Documents/InEarSnitch/inearsnitch.db` also exists.
- **Default Database Parameter in `database.py`**:
  - Path: `/Users/ben/Desktop/InEarSnitch/database.py:5`
  - Code: `class DatabaseManager: def __init__(self, db_path="inearsnitch.db"):`
  - Hazard: Instantiating `DatabaseManager()` without arguments in `/Users/ben/Desktop/InEarSnitch` directly targets the 16.38 MB production/dev database.
- **Smoke Test Status**:
  - Command: `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`
  - Output:
    ```
    🔍 SMOKE TEST — InEar Snitch
    1️⃣  Syntax Check: 4/4 passed
    2️⃣  Critical Imports: 2/2 passed
    3️⃣  Critical Widget References (main.py): 9/9 passed
    4️⃣  Data Flow & Anti-Regression: 4/4 passed
    ==================================================
    ✅ ALL 19 CHECKS PASSED
    ==================================================
    ```

### 1.2 Inspection of Target Test Suites in `tests/test_prokit_e2e.py`
The E2E test suite at `/Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py` contains 87 test cases. The specific classes and methods relevant to Milestone 2 (R2 database.py) are:

1. **`TestTier1DBSchema` (Lines 207–310)**:
   - `test_tipprofiles_table_schema`: Asserts `TipProfiles` exists with columns: `id`, `name`, `material`, `color_hex`, `icon_char`, `is_default`.
   - `test_tipprofiles_seed_data_deterministic_order`: Asserts `TipProfiles` seeded deterministically with:
     - id=1: "Unbekannt"
     - id=2: "Kein Aufsatz"
     - id=3: "Standard Foam"
     - id=4: "ProKit V1"
     - id=5: "ProKit V2" (with `is_default == 1`)
   - `test_measurements_has_tip_id_column`: Asserts `Measurements` table has column `tip_id` with default value `'1'`.
   - `test_db_migration_idempotent`: Repeated calls to `_init_db()` do not create duplicate seed rows (count remains 5, id=1 count is 1).
   - `test_legacy_measurements_backfilled_to_unknown`: Creates legacy DB with 3 measurements without `tip_id`, runs `DatabaseManager(isolated_db_path)`, asserts all 3 records have `tip_id == 1`.

2. **`TestTier1DBQueries` (Lines 312–406)**:
   - `test_get_all_tips_include_and_exclude_unknown`:
     - `get_all_tips(include_unknown=True)` returns 5 items (including id=1).
     - `get_all_tips(include_unknown=False)` returns 4 items (excluding id=1).
     - Returns list of dictionaries with keys: `id`, `name`, `material`, `color_hex`, `icon_char`, `is_default`.
   - `test_save_measurement_persists_tip_id`:
     - Calls `save_measurement(..., tip_id=4)` and verifies column `tip_id` in `Measurements` is 4.
   - `test_get_last_used_tip_excludes_unknown`:
     - If only tip_id=1 exists -> returns `None`.
     - If tip_id=4 saved -> returns `4`.
     - If tip_id=5 saved -> returns `5`.
     - If subsequent measurement saved with tip_id=1 -> still returns `5` (must exclude id=1).
   - `test_get_reproducibility_scores_structure`:
     - With 6 measurements, returns dict `{'left': {...}, 'right': {...}}`.
     - Channel dict contains: `count == 6`, `is_preliminary == True` (since 6 < 10), and `isinstance(score, float)`.
   - `test_get_seal_history_delta_and_status`:
     - Returns dict `{'left': [...], 'right': [...]}` with chronological seal records.
     - Record keys: `id`, `timestamp`, `delta_db`, `val_40`, `val_500`, `seal_ok`, `status`.
     - Delta >= -12.0 dB: `seal_ok=True`, `status="OK"`.
     - Delta < -12.0 dB: `seal_ok=False`, `status="LEAK"`.

3. **`TestTier2DBBoundaries` (Lines 674–760)**:
   - `test_bulk_legacy_migration_500_records`: 500 legacy measurements with NULL tip_id all backfilled to `tip_id=1`, 0 remaining NULL.
   - `test_seed_tips_preserve_existing_records`: If `TipProfiles` already contains custom id=1 (`Custom Unknown`), migration does not overwrite or wipe it.
   - `test_save_measurement_none_tip_id_defaults_to_1`: `save_measurement(..., tip_id=None)` safely stores `1`.
   - `test_get_last_used_tip_nonexistent_iem`: Querying unknown IEM or `None` returns `None`.
   - `test_db_init_on_empty_string_path`: `DatabaseManager(":memory:")` initializes cleanly.

4. **`TestTier2DSPBoundaries` (Lines 761–868)**:
   - `test_reproducibility_band_limited_ignores_above_8khz`: Identical curves below 8 kHz with massive 30 dB variations above 8 kHz yield `score == 0.0` (proves strict 20 Hz – 8 kHz band-limiting per Design Decision 5).
   - `test_reproducibility_mono_only_left`: When `mag_r is None`, `scores["left"]` is computed and `scores["right"] is None`.
   - `test_reproducibility_mono_only_right`: When `mag_l is None`, `scores["left"] is None` and `scores["right"]` is computed.
   - `test_reproducibility_solid_threshold_10_measurements`: With N=10 measurements, `is_preliminary == False`.
   - `test_reproducibility_mismatched_frequency_bins_interpolation`: Handles differing sample rates (e.g. 44.1 kHz grid with 15000 points vs 48 kHz grid with 24001 points) via common grid interpolation (e.g. `np.interp`).
   - `test_seal_history_empty_and_corrupt_blobs_skipped`: Empty or corrupt BLOBs are skipped without unhandled unpack exceptions.
   - `test_seal_threshold_exact_boundary`: Exact boundary verification (-11.99 dB -> `seal_ok=True`, -12.01 dB -> `seal_ok=False`).

5. **`test_unlock_and_db_catalog_interaction` (Lines 1059–1067)**:
   - ProKit unlocked -> `isolated_db.get_all_tips(include_unknown=False)` returns 4 catalog tips.

6. **Additional M2-Interacting Tests**:
   - `test_reproducibility_isolated_per_tip` (Lines 1143–1164): Different tips for the same IEM maintain independent score calculations.
   - `test_multi_iem_tip_persistence_and_suggestion` (Lines 1128–1141): Multiple IEM models preserve independent last-used tips.
   - `test_scenario_legacy_migration_and_compatibility` (Lines 1251–1308): Full roundtrip migration of legacy database and subsequent queries.
   - `test_scenario_statistical_reproducibility` (Lines 1309–1337): 12 measurements with HF noise, confirms band-limiting and `is_preliminary=False`.
   - `test_scenario_seal_leak_detection_and_degradation` (Lines 1338–1370): Chronological leak detection across multiple insertions.

### 1.3 Current Test Execution Results
- Command: `pytest -v tests/test_prokit_e2e.py -k "TestTier1DBSchema or TestTier1DBQueries or TestTier2DBBoundaries or TestTier2DSPBoundaries or test_unlock_and_db_catalog_interaction"`
- Result: **20 failed, 3 passed, 64 deselected**.
  - All 5 `TestTier1DBSchema` tests failed (`sqlite3.OperationalError: no such table: TipProfiles`, `AssertionError: assert 'id' in {}`, `sqlite3.OperationalError: no such column: tip_id`).
  - All 5 `TestTier1DBQueries` tests failed (`AttributeError: 'DatabaseManager' object has no attribute 'get_all_tips'`, `TypeError: save_measurement() got an unexpected keyword argument 'tip_id'`).
  - 2 `TestTier2DBBoundaries` failed (`test_bulk_legacy_migration_500_records`, `test_save_measurement_none_tip_id_defaults_to_1`).
  - All 7 `TestTier2DSPBoundaries` failed (`TypeError: save_measurement() got an unexpected keyword argument 'tip_id'`).
  - 1 `TestTier3CrossFeatureCombinations` failed (`test_unlock_and_db_catalog_interaction`).

---

## 2. Logic Chain

1. **Isolation Verification**:
   - In `tests/test_prokit_e2e.py`, tests consume the `isolated_db_path` and `isolated_db` pytest fixtures (lines 84–97).
   - `isolated_db_path` leverages pytest's `tmp_path` fixture to create a temporary database in `/private/var/folders/.../T/pytest-.../`.
   - Therefore, running `pytest tests/test_prokit_e2e.py` never interacts with or alters `/Users/ben/Desktop/InEarSnitch/inearsnitch.db`.
2. **Accidental Production DB Mutation Hazard**:
   - Because `DatabaseManager(db_path="inearsnitch.db")` defaults to a local file, any ad-hoc worker script that calls `DatabaseManager()` without arguments will open and migrate `/Users/ben/Desktop/InEarSnitch/inearsnitch.db`.
   - To guarantee safety:
     - Worker scripts must strictly use `tempfile.NamedTemporaryFile(suffix=".db")` or `:memory:`.
     - Reviewers must verify that `DatabaseManager` instantiation in all test scripts explicitly supplies the temporary path.
3. **Deterministic Seeding & Migration Safety**:
   - `_init_db()` must execute `CREATE TABLE IF NOT EXISTS TipProfiles (...)`.
   - `ALTER TABLE Measurements ADD COLUMN tip_id INTEGER DEFAULT 1` must be wrapped in `try/except sqlite3.OperationalError: pass`.
   - `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL` must run after the column is added to guarantee backward compatibility with pre-existing records.
   - Seed data insertion must use `INSERT OR IGNORE INTO TipProfiles (id, name, material, color_hex, icon_char, is_default)` to be idempotent across multiple calls and prevent overwriting custom entries.
4. **DSP & Reproducibility Safety Rules**:
   - `mag_l` and `mag_r` can be `None` or `b''` in partial or mono sweeps. The query must handle missing channel BLOBs gracefully without throwing unpack or interpolation errors.
   - Interpolation (`np.interp`) onto a common grid between 20 Hz and 8000 Hz is required because sweeps may have different bin counts (e.g., 44.1 kHz vs 48 kHz).
   - The standard deviation must be evaluated frequency-bin by frequency-bin across sweeps, and the overall score is the mean across 20–8000 Hz.
   - Scores must return `None` if fewer than 5 valid curves exist for a given channel.
   - `is_preliminary` must be `True` if 5 <= count < 10, and `False` if count >= 10.
5. **Smoke Test Invariance**:
   - `smoke_test.py` validates AST syntax of `main.py`, `analysis_ui.py`, `audio_engine.py`, and `analysis.py`, plus UI widget names and data flow references.
   - Adding methods and migration logic to `database.py` does not alter any of the 19 checks in `smoke_test.py`.
   - `smoke_test.py` must be executed before and after any commit.

---

## 3. Caveats

1. **No UI or App Gate Modifications in M2**: Milestone 2 is scoped strictly to `database.py`. The bottom-bar UI combobox, history badges, and diagnostics cards are M3, M4, and M5 scopes. The worker must only edit `database.py`.
2. **Legacy Measurement Unpacking**: Existing measurements in `inearsnitch.db` store numpy float64 byte arrays. If an older measurement has corrupt or empty BLOBs, `np.frombuffer` must be safely protected with a length check / try-except to avoid breaking seal or reproducibility calculations.
3. **Default tip_id Handling**: When callers invoke `save_measurement(..., tip_id=None)`, the method must coerce `tip_id` to `1` ("Unbekannt").

---

## 4. Conclusion & Actionable Recommendations

### Recommended Worker Implementation Blueprint for `database.py`

#### 1. Schema & Migration (`_init_db`)
```python
# In database.py: DatabaseManager._init_db()

# Create TipProfiles table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS TipProfiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        material TEXT,
        color_hex TEXT,
        icon_char TEXT,
        is_default INTEGER DEFAULT 0
    )
""")

# Safe migration: add tip_id to Measurements
try:
    cursor.execute("ALTER TABLE Measurements ADD COLUMN tip_id INTEGER DEFAULT 1")
except sqlite3.OperationalError:
    pass

# Backfill legacy measurements
try:
    cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")
except sqlite3.OperationalError:
    pass

# Deterministic Seed Data (INSERT OR IGNORE ensures idempotency and preserves existing id=1)
seed_tips = [
    (1, "Unbekannt", "Standard", "#6b7280", "?", 0),
    (2, "Kein Aufsatz", "None", "#94a3b8", "○", 0),
    (3, "Standard Foam", "Foam", "#f59e0b", "●", 0),
    (4, "ProKit V1", "Silicone", "#3b82f6", "◆", 0),
    (5, "ProKit V2", "Silicone", "#10b981", "★", 1),
]
cursor.executemany("""
    INSERT OR IGNORE INTO TipProfiles (id, name, material, color_hex, icon_char, is_default)
    VALUES (?, ?, ?, ?, ?, ?)
""", seed_tips)
```

#### 2. `save_measurement` Extension
```python
def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, 
                     gain_db="", notes="", photo_path="", tip_id=1):
    if tip_id is None:
        tip_id = 1
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    ml = mag_l.tobytes() if mag_l is not None else b''
    mr = mag_r.tobytes() if mag_r is not None else b''
    pl = phase_l.tobytes() if phase_l is not None else b''
    pr = phase_r.tobytes() if phase_r is not None else b''
    f_bytes = freqs.tobytes() if freqs is not None else b''
    
    cursor.execute("""
        INSERT INTO Measurements 
        (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path, tip_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (iem_id, gain_db, f_bytes, ml, mr, pl, pr, notes, photo_path, tip_id))
    conn.commit()
    conn.close()
```

#### 3. Query APIs
```python
def get_all_tips(self, include_unknown=True):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    if include_unknown:
        cursor.execute("SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles ORDER BY id ASC")
    else:
        cursor.execute("SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles WHERE id != 1 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "material": r[2],
            "color_hex": r[3],
            "icon_char": r[4],
            "is_default": bool(r[5])
        }
        for r in rows
    ]

def get_last_used_tip(self, iem_id):
    if iem_id is None:
        return None
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tip_id FROM Measurements 
        WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1 
        ORDER BY timestamp DESC, id DESC LIMIT 1
    """, (iem_id,))
    row = cursor.fetchone()
    conn.close()
    return int(row[0]) if row and row[0] is not None else None
```

#### 4. DSP APIs (`get_reproducibility_scores` & `get_seal_history`)
- **`get_reproducibility_scores(iem_id, tip_id)`**:
  - Grid: `common_f = np.linspace(20.0, 8000.0, 800)`
  - Query measurements with non-null BLOBs for `iem_id` and `tip_id`.
  - Process Left and Right separately.
  - Skip empty / corrupt arrays (`len < 10`).
  - Interpolate valid arrays onto `common_f`: `interp_mags = [np.interp(common_f, f, m) for f, m in channel_curves]`.
  - If `len(interp_mags) < 5`: channel result is `None`.
  - If both Left and Right are `None`: return `None`.
  - Std dev across curves: `std_per_bin = np.std(np.array(interp_mags), axis=0, ddof=0)` (identical curves -> std=0.0).
  - Score: `mean_std = float(round(np.mean(std_per_bin), 2))`
  - Result dict per valid channel: `{"score": mean_std, "std_dev": mean_std, "count": len(interp_mags), "is_preliminary": bool(len(interp_mags) < 10)}`.
  - Return `{"left": left_res, "right": right_res}`.
- **`get_seal_history(iem_id, tip_id)`**:
  - Query `id, timestamp, frequencies, magnitude_l, magnitude_r FROM Measurements WHERE iem_id = ? AND tip_id = ? ORDER BY timestamp ASC, id ASC`.
  - For each channel:
    - If BLOB is empty/corrupt, skip.
    - `idx_40 = (f >= 35.0) & (f <= 45.0)`
    - `idx_500 = (f >= 450.0) & (f <= 550.0)`
    - `val_40 = float(np.mean(m[idx_40]))`
    - `val_500 = float(np.mean(m[idx_500]))`
    - `delta_db = float(round(val_40 - val_500, 2))`
    - `seal_ok = bool(delta_db >= -12.0)`
    - `status = "OK" if seal_ok else "LEAK"`
    - Append dict to channel list.
  - Return `{"left": left_list, "right": right_list}`.

---

## 5. Verification Method

### 5.1 Primary Test Commands for Worker and Reviewers

1. **Smoke Test Guard (Mandatory Before & After)**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 smoke_test.py
   ```
   *Acceptance Criteria*: Must pass 19/19 checks (`✅ ALL 19 CHECKS PASSED`).

2. **Milestone 2 Isolated E2E Test Suite**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && pytest -v tests/test_prokit_e2e.py -k "TestTier1DBSchema or TestTier1DBQueries or TestTier2DBBoundaries or TestTier2DSPBoundaries or test_unlock_and_db_catalog_interaction or test_reproducibility_isolated_per_tip or test_multi_iem_tip_persistence_and_suggestion or test_scenario_legacy_migration_and_compatibility or test_scenario_statistical_reproducibility or test_scenario_seal_leak_detection_and_degradation"
   ```
   *Acceptance Criteria*: **24 passed, 0 failed, 63 deselected** (100% pass of all M2 database targets).

3. **Ad-hoc / Scratch Script Isolation Protocol**:
   When writing manual verification scripts, Worker MUST use a temporary database:
   ```python
   import tempfile
   import os
   from database import DatabaseManager

   with tempfile.TemporaryDirectory() as tmp_dir:
       temp_db_path = os.path.join(tmp_dir, "scratch_test.db")
       db = DatabaseManager(temp_db_path)
       # Verify methods here
   ```
   *Never run `DatabaseManager()` without arguments.*

4. **Production Database Invariance Verification**:
   Before and after Worker commits, verify file size and hash/timestamp of the repository database:
   ```bash
   ls -la /Users/ben/Desktop/InEarSnitch/inearsnitch.db
   ```
   *Acceptance Criteria*: Size must remain exactly `16379904` bytes.

### 5.2 Invalidation Conditions
- Any test failing in `TestTier1DBSchema`, `TestTier1DBQueries`, `TestTier2DBBoundaries`, or `TestTier2DSPBoundaries`.
- Modification or corruption of `/Users/ben/Desktop/InEarSnitch/inearsnitch.db`.
- Drop in `smoke_test.py` below 19/19 passing checks.
- Any merge of Left and Right channel metrics into a combined value.
- Failure to band-limit reproducibility strictly to 20 Hz – 8000 Hz.
