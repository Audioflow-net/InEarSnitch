# InEarSnitch ProKit Tip-Tracking — Core & DB Technical Investigation Report

**Author:** Core & DB Explorer (`explorer_survey_db_1`)  
**Target Files:** `config.py`, `database.py`, `smoke_test.py`  
**Date:** 2026-09-22  

---

## 1. Observation

### 1.1 `config.py` Architecture & Persistence
Direct inspection of `/Users/ben/Desktop/InEarSnitch/config.py` (lines 1–24) reveals:
- Line 4–13: `get_data_dir()` resolves to `os.path.join(os.path.expanduser("~"), "Documents", "InEarSnitch")`. It verifies existence and creates the directory if missing via `os.makedirs(app_dir)`.
- Line 15–23: `get_db_path()` returns `"inearsnitch.db"` in development mode, or `Documents/InEarSnitch/inearsnitch.db` if `getattr(sys, 'frozen', False)`.
- The ProKit unlock persistence target is specified in `/Users/ben/Desktop/InEarSnitch/.agents/rules/prokit_system.md` (lines 13, 19–20) as `get_data_dir() + '/.prokit_unlocked'`.
- There are currently no unlock functions or hashes in `config.py`.

### 1.2 `database.py` Architecture & Existing Schema
Direct inspection of `/Users/ben/Desktop/InEarSnitch/database.py` (lines 1–133) and database inspection on `inearsnitch.db` reveals:
- **Connection Lifecycle:** `DatabaseManager` does NOT maintain a persistent connection or connection pool. Every method (`_init_db`, `save_measurement`, `load_reference_measurement`) opens a fresh connection with `conn = sqlite3.connect(self.db_path)`, performs work, commits, and explicitly closes via `conn.close()`. Default path is `db_path="inearsnitch.db"`.
- **Existing Tables:**
  - `Musicians` (id, name, band, notes, profile_pic)
  - `IEM_Models` (id, musician_id, model_name, serial_number, contact_person, service_notes, iem_pic, abbreviation, custom_name, color)
  - `Measurements` (id, iem_id, timestamp, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path)
  - Also dynamically added by UI modules: `meas_name` in `history_ui.py:475`, `AppSettings` in `main.py`, `eq_presets` in `analysis_ui.py:941`.
- **Existing Migration Pattern:**
  - Performed in `_init_db()` using individual `try / except sqlite3.OperationalError: pass` around `ALTER TABLE` statements (e.g. lines 25–32, 50–53, 74–81):
    ```python
    try:
        cursor.execute("ALTER TABLE IEM_Models ADD COLUMN color TEXT DEFAULT '#2a2a2a'")
    except sqlite3.OperationalError:
        pass
    ```
- **`save_measurement()` Implementation:**
  - Lines 86–107:
    ```python
    def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path=""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        ml = mag_l.tobytes() if mag_l is not None else b''
        mr = mag_r.tobytes() if mag_r is not None else b''
        pl = phase_l.tobytes() if phase_l is not None else b''
        pr = phase_r.tobytes() if phase_r is not None else b''
        f_bytes = freqs.tobytes() if freqs is not None else b''
        cursor.execute("""
            INSERT INTO Measurements 
            (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (iem_id, gain_db, f_bytes, ml, mr, pl, pr, notes, photo_path))
        conn.commit()
        conn.close()
    ```
  - Callers in codebase:
    1. `main.py:3858` in `save_trace_to_db()`: calls `self.db.save_measurement(self.current_iem_id, self.temp_freqs, self.temp_mag_l, self.temp_mag_r, self.temp_phase_l, self.temp_phase_r, gain, notes, "")`.
    2. `history_ui.py:430`: executes an inline raw SQL `INSERT INTO Measurements` during file import.
- **BLOB Storage & Signal Structure:**
  - NumPy arrays are converted directly to raw IEEE 754 float64 byte strings using `array.tobytes()`.
  - Empty or missing arrays are stored as `b''` (empty byte BLOB).
  - Unpacking in `load_reference_measurement()` (lines 126–128) and `history_ui.py:500–502` uses `np.frombuffer(blob, dtype=np.float64) if blob else None`.
  - Inspection of actual stored records in `inearsnitch.db` showed:
    - ID 1–5: `f_len=24001, ml_len=24001, mr_len=0` (Left-channel only measurement)
    - ID 24–25: `f_len=33076, ml_len=33076, mr_len=33076` (Stereo measurement at 44.1 kHz)
    - ID 26: `f_len=72001, ml_len=0, mr_len=72001` (Right-channel only measurement at 96 kHz)
  - Key finding: Frequency vectors can vary in bin count and step size between different measurements of the same IEM due to differing soundcard sample rates.

### 1.3 `smoke_test.py` Verification
Direct execution of `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`:
- 19/19 checks PASSED.
- Check groups:
  1. Syntax check (`main.py`, `analysis_ui.py`, `audio_engine.py`, `analysis.py`)
  2. Critical Imports (`main.py` PySide6, `analysis_ui.py` pyqtgraph)
  3. Critical Widget References (`self.btn_capture`, `self.btn_trace`, `self.btn_save_db`, `self.btn_rta_raw`, `self.btn_iec_guide`, `self.cb_meas_target`, `self.cb_meas_history`, `self.plot_widget`, `self.page_ana`)
  4. Data Flow & Anti-Regression (`temp_mag_l`, `target_freqs`, `_last_dial_val`, `WA_TransparentForMouseEvents`)
- `config.py` and `database.py` are NOT directly checked by `smoke_test.py`, but all changes to them must preserve the interfaces expected by `main.py`, `analysis_ui.py`, and `history_ui.py`.

---

## 2. Logic Chain

### 2.1 Unlock-System Design (`config.py`)
1. **Observation:** `ORIGINAL_REQUEST.md` (lines 29–87) specifies three functions (`is_prokit_unlocked()`, `unlock_prokit(code)`, `revoke_prokit()`), 50 pre-calculated SHA256 hashes, and persistence to `.prokit_unlocked` in `get_data_dir()`.
2. **Path Resolution:** Calling `os.path.join(get_data_dir(), ".prokit_unlocked")` provides a uniform, platform-independent path on macOS and Windows (`~/Documents/InEarSnitch/.prokit_unlocked`).
3. **Validation Flow:**
   - Input code is normalized: `code.strip().upper()` (all generated codes follow `SNITCH-PROKIT-2024-XXX`).
   - SHA256 hash computed: `hashlib.sha256(norm_code.encode('utf-8')).hexdigest().lower()`.
   - Membership check against hardcoded set `VALID_CODE_HASHES`.
   - On match: write the hash to `.prokit_unlocked` file, return `True`.
   - On mismatch: leave file untouched, return `False`.
4. **Revocation & Query:**
   - `is_prokit_unlocked()` checks `os.path.exists(unlock_file_path)`.
   - `revoke_prokit()` removes the file if present via `os.remove()`, returning `True`.

### 2.2 Table Architecture & Seed Data (`database.py`)
1. **Observation:** `ORIGINAL_REQUEST.md` (lines 20–22, 91–93, 126–127) requires:
   - Freitext is strictly forbidden; all tips belong to `TipProfiles`.
   - Seed data must insert "Unbekannt" FIRST (`id=1`).
   - Seeds: "Unbekannt", "Kein Aufsatz", "Standard Foam", "ProKit V1", "ProKit V2".
   - `Measurements` must have `tip_id` referencing `TipProfiles(id)`.
   - All legacy records (`tip_id IS NULL`) must be updated to `tip_id = 1`.
2. **Schema Definition for `TipProfiles`:**
   ```sql
   CREATE TABLE IF NOT EXISTS TipProfiles (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT NOT NULL,
       material TEXT,
       color_hex TEXT,
       icon_char TEXT,
       is_default INTEGER DEFAULT 0
   );
   ```
3. **Seed Insertion Strategy:**
   To guarantee that "Unbekannt" is permanently assigned `id=1` across fresh installs and migrations:
   ```sql
   INSERT OR IGNORE INTO TipProfiles (id, name, material, color_hex, icon_char, is_default)
   VALUES 
       (1, 'Unbekannt', 'None', '#6b7280', '?', 0),
       (2, 'Kein Aufsatz', 'None', '#9ca3af', 'Ø', 0),
       (3, 'Standard Foam', 'Foam', '#f59e0b', '☁', 0),
       (4, 'ProKit V1', 'TPU', '#3b82f6', '◆', 0),
       (5, 'ProKit V2', 'TPU', '#10b981', '★', 1);
   ```
   Specifying explicit primary keys `1, 2, 3, 4, 5` with `INSERT OR IGNORE` ensures deterministic IDs.
4. **Migration & Legacy Backfill Execution in `_init_db()`:**
   - Add column safely:
     ```python
     try:
         cursor.execute("ALTER TABLE Measurements ADD COLUMN tip_id INTEGER REFERENCES TipProfiles(id) DEFAULT 1")
     except sqlite3.OperationalError:
         pass
     ```
   - Run backfill immediately after table creation and column addition:
     ```python
     cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")
     ```
   - For newly created databases, update `CREATE TABLE IF NOT EXISTS Measurements` to declare `tip_id INTEGER DEFAULT 1 REFERENCES TipProfiles(id)`.

### 2.3 `save_measurement()` Signature Extension
1. **Observation:** `main.py:3858` passes 9 positional arguments: `(iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain, notes, "")`.
2. **Backward Compatibility:** Adding `tip_id=1` with default value 1 ensures existing positional calls do not break.
   ```python
   def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path="", tip_id=1):
   ```
3. In the SQL query:
   ```sql
   INSERT INTO Measurements 
   (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path, tip_id)
   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
   ```
   Passing `tip_id if tip_id is not None else 1`.

### 2.4 New Query & Statistical Methods

#### A. `get_all_tips(include_unknown=True)`
Returns list of dictionaries ordered by `id ASC`. When `include_unknown=False`, filters `WHERE id != 1` for UI dropdowns where "Unbekannt" shouldn't be selectable for new measurements.

#### B. `get_last_used_tip(iem_id)`
- Must exclude `id=1` ("Unbekannt") as specified in R2.
- Query:
  ```sql
  SELECT tip_id FROM Measurements
  WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
  ORDER BY timestamp DESC, id DESC
  LIMIT 1
  ```
- Returns `int` (`tip_id`) or `None` if no non-legacy tip has been used for this IEM.

#### C. `get_reproducibility_scores(iem_id, tip_id)`
- **Constraints:**
  - Band-limited to 20 Hz – 8000 Hz. Coupler resonances above 8 kHz cause non-reproducible shifts.
  - L and R channels must be computed strictly separately.
  - Minimum 5 measurements required per channel; below 5 returns `None`.
  - 5–9 measurements flags `is_preliminary = True`.
- **Handling Inconsistent Frequency Sampling:**
  Because measurements in `inearsnitch.db` have varying bin counts (e.g. 24001 at 48 kHz vs 33076 at 44.1 kHz), curves cannot be directly subtracted element-wise without interpolation.
  - Solution: Define standard psychoacoustic logarithmic grid:
    `common_grid = np.geomspace(20.0, 8000.0, 500)`
  - Interpolate each measurement curve: `np.interp(common_grid, f_meas, mag_meas)`
  - Form matrix of shape `(N, 500)`.
  - Compute standard deviation per frequency bin with Bessel's correction (`ddof=1`): `stds = np.std(matrix, axis=0, ddof=1)`.
  - Mean standard deviation across the 20–8000 Hz band: `score = float(np.mean(stds))`.
- **Return Contract:**
  If neither channel has $\ge 5$ measurements: returns `None`.
  Otherwise returns:
  ```python
  {
      "left": {
          "score": float,            # Mean std dev in dB (20-8000 Hz)
          "std_dev": float,          # Alias
          "count": int,              # Number of measurements used
          "is_preliminary": bool     # True if 5 <= count < 10
      } if count_l >= 5 else None,
      "right": {
          "score": float,
          "std_dev": float,
          "count": int,
          "is_preliminary": bool
      } if count_r >= 5 else None
  }
  ```

#### D. `get_seal_history(iem_id, tip_id)`
- **Constraints:**
  - Compute 40 Hz vs 500 Hz delta over time from stored BLOBs.
  - L and R channels must be strictly separate.
  - Acoustic criteria from `main.py:3466-3476`:
    - 40 Hz band: 35 Hz to 45 Hz (`(freqs >= 35) & (freqs <= 45)`)
    - 500 Hz band: 450 Hz to 550 Hz (`(freqs >= 450) & (freqs <= 550)`)
    - $\Delta = \text{mean}(mag_{40}) - \text{mean}(mag_{500})$
    - Seal status: $\Delta \ge -12.0\text{ dB} \rightarrow \text{"OK"}$; $\Delta < -12.0\text{ dB} \rightarrow \text{"LEAK"}$.
- **Return Contract:**
  Returns dictionary with `left` and `right` lists containing timestamp, delta, seal status:
  ```python
  {
      "left": [
          {"id": int, "timestamp": str, "delta_db": float, "val_40": float, "val_500": float, "seal_ok": bool, "status": "OK" | "LEAK"}
      ],
      "right": [
          {"id": int, "timestamp": str, "delta_db": float, "val_40": float, "val_500": float, "seal_ok": bool, "status": "OK" | "LEAK"}
      ]
  }
  ```

---

## 3. Caveats

1. **Mono vs Stereo Measurements:** In real sessions, musicians often measure only Left or only Right at a given moment. The implementation must not assume that both channels exist in a row. Left and Right must be processed independently.
2. **Frequency Alignment:** Measurements taken under different hardware configurations (44.1 kHz vs 48 kHz vs 96 kHz) have different frequency resolutions. Performing `np.interp` on `np.geomspace(20, 8000, 500)` solves this completely and avoids length-mismatch exceptions.
3. **Direct SQL in `history_ui.py`:** Line 430 of `history_ui.py` bypasses `DatabaseManager.save_measurement()` and executes an inline `INSERT INTO Measurements`. Because our database schema defines `tip_id INTEGER DEFAULT 1`, this inline insert will safely assign `tip_id = 1` without errors. However, UI implementers should be informed so `history_ui.py` can be updated to include `tip_id` during file import.
4. **UI Decoupling:** `database.py` should remain pure Python + SQLite + NumPy with zero Qt/PySide6 dependencies. All Qt UI binding logic belongs in `main.py`, `history_ui.py`, and `analysis_ui.py`.

---

## 4. Conclusion & Proposed Implementations

### 4.1 Proposed `config.py` Additions

```python
import os
import sys
import hashlib

# 50 Pre-generated ProKit unlock hashes (SNITCH-PROKIT-2024-001 through -050)
VALID_CODE_HASHES = {
    "1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2",
    "28c967ffdb947142ba96b211ac9b7a82d73e705ae4938b0048357842160ccca5",
    "467080d8304ae74587a8871d277301d6962350cc8d0adbdeacf164992306749e",
    "3340498b45cedd29a0f3e4bd16bc218e6642b2617966ac0bb992a4db2f643577",
    "752ec0de4e8783a1a9b6cea3727a875fce76fdc815c0188b53c42e090b6a6d49",
    "2d4daa3506a61e12f3e6bdcf812d381923313ce48c4c3261fe9eea85b48f8478",
    "fa19fa327ec49524a82509d8ece545cf599d41cbcedd120d94fa2fbe4ae67cf7",
    "2bd13e963d452a752e565da583a8e68055d2a98f106d1dd258a3ad795c177d0b",
    "9adb031d8be54cbf43003cc488add1f8f855e0dff40f6d4d02728107467c9bf7",
    "8329c956d34a3065c16c9fce051d318f48f59e3a168514ec118e784b2afd8aad",
    "bc688e2817772af9de241f6ccc18610c8ef7fb8804c27dd57ac360630dac498a",
    "a66191e82cd3095c357aaf3425269ca732e3f08e5fda033cc60a0af2a9b1cdf5",
    "766545bc887e483e9c41b204fbcf985763398ede9d7f731d6c17926cc094472c",
    "5903d43d01d796973d727dcf4914f654607428045aa0c4dddf44f8bc36ccc143",
    "25510b6e524bc19381508ebadde8a40e142dfd2db4f77b09170b92f87f724d2a",
    "0caec3efc96458f024248206516790cf9fd52aabb29cb4a5c9263d1bdaec0deb",
    "24bd2789b55de96bbf6a312680f6a1e282555eeb200b91b6d97d9290b548590c",
    "7d7f06121b54cdc34163f9c520f1a86d802c992580f515355a89a4e0bad75e42",
    "12fd82d9bfef2250bc8eca14a5578abf7db236a90fe779a495b4da8ad8bade28",
    "c433deca515974a48aa7d353482c57e5726e0f8830a0b5cd8401fc24ecef05bc",
    "f7180a263f1ca78f52bb304194a41d43ca9592591dfd9913f660a62c945b37e7",
    "ee7bd1d3904f1980bb93a778146265675321266cf12b34f213d111aa95b324e1",
    "7ea57abff314366f97a88d26cd1fe211432b463cc1b3bab5086e7c9d38a57584",
    "77f89e8a6ccad0efb0a93af8c55deba0b6bb8143e443c434086b5588a5d4c392",
    "02fdbd04dfa0b206c050030c0fde369c13b63826609b57629bc11eebc1b07953",
    "fb7bc08e304bc9f285deb479e7f2809f7878ed699571864663cd42a585712088",
    "5db52172b22bc0bb2839f3b6152db1ee40330259b061a97af317daef71f74cab",
    "c447ab57a79b5a0585c7fdea5bf960e6cad82504fc7d3779974c0ef6eff97cb8",
    "4f542e2e655cd4c549086585f1b35e4791a642dc48928b6678dbc61545daa06c",
    "9c5a61b5d71129cd60ad54432cf05bb51e197bcab379dfe3580298da4ac8405d",
    "b078f28b7df0f1309b46ff7f60f07dbf556de84e2f94d401f4cb76e735250ce1",
    "fe2fbfabd552d26935d42bab0363afea0fcf836e37cd5bf443fac45dcec2b301",
    "7ecb10814cce4353c5755321e58eaee1c7903517ec47ee1b7e885c74cbbb1eeb",
    "574ad449c2b3d44a819541c04f949b7da88726c88cdea706f3861c28c26eed75",
    "137648325202aa6877ef61d5a3676be21f6984d76825c228cd54cbeccbd1515a",
    "ee2cdd6fdac8c38e2407464045ae904bd3226744535961dfb62769f3644e5f2c",
    "144fb12c8c3153380ded932b955b1faf0eb630a0f92a5c9ad2b856ae128b7285",
    "b75abc7d948c7988501b6956ec5c73b2f3a7ba4331ff4625324056a12e8f827c",
    "f158ff3e0ffbb5cb70ec6ff3b5a9eeaf1c313aee6d74a0ad3c901db5becd96e0",
    "ff443743ef2e6039023ae4dc835a86a580287565c2d49f02734024cc9afee42b",
    "ad0e8d419b1647e5966034565f2494b646e4f1a36e1cbb807e9621ccf4249c7e",
    "4ed91365b766ec8fcd7a5cb4b34455255be226619a331b43062a78f704cb844b",
    "dbbb84b2101da22a25153e7fc97ceaa08592b28cfd32803c9068f85893633172",
    "07a30ae449aaec190e5307da93ddb1dc6d1c6c649e7f677e4f6be995f5a98a44",
    "8ca06be4b4c080a7343aafb358406adafe205581f7e4fd80680c78ef513ccba8",
    "3f43ab77a551d55e2d852c581d77fd1c6601ea961e747ced419027506a96d656",
    "49aff215aa8ed742bec2ebb5bdd7fe8d0b2ed4457e86f0be0c2c77209a3efe31",
    "f02975c34add7e5b646fda9731643b7af58216660cebf4d1e649f13d4f471e7b",
    "4d58450d5e89ab7d28ccd55a62d026034c8f1e10efa2b89347e1d2bd76237faa",
    "beb4fa70979bc164202352ec89574193cbdba08a5f2c6c5ff74088acd7600e7a",
}

def get_unlock_file_path() -> str:
    """Returns absolute path to the .prokit_unlocked persistence file."""
    return os.path.join(get_data_dir(), ".prokit_unlocked")

def is_prokit_unlocked() -> bool:
    """Checks whether the offline ProKit feature gate is unlocked."""
    return os.path.exists(get_unlock_file_path())

def unlock_prokit(code: str) -> bool:
    """
    Attempts to unlock the ProKit gate using the provided unlock code.
    If SHA256 matches VALID_CODE_HASHES, creates .prokit_unlocked and returns True.
    """
    if not code or not isinstance(code, str):
        return False
    norm_code = code.strip().upper()
    h = hashlib.sha256(norm_code.encode("utf-8")).hexdigest().lower()
    if h in VALID_CODE_HASHES:
        try:
            target_path = get_unlock_file_path()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(h + "\n")
            return True
        except Exception:
            return False
    return False

def revoke_prokit() -> bool:
    """
    Revokes ProKit unlock state by deleting .prokit_unlocked.
    Returns True if successfully removed or already absent.
    """
    target_path = get_unlock_file_path()
    try:
        if os.path.exists(target_path):
            os.remove(target_path)
        return True
    except Exception:
        return False
```

### 4.2 Proposed `database.py` Implementation

#### Schema updates in `_init_db()`:
```python
        # TipProfiles entity for coupler ear tips catalog
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

        # Insert seed data deterministically (Unbekannt ALWAYS gets id=1)
        seed_tips = [
            (1, "Unbekannt", "None", "#6b7280", "?", 0),
            (2, "Kein Aufsatz", "None", "#9ca3af", "Ø", 0),
            (3, "Standard Foam", "Foam", "#f59e0b", "☁", 0),
            (4, "ProKit V1", "TPU", "#3b82f6", "◆", 0),
            (5, "ProKit V2", "TPU", "#10b981", "★", 1),
        ]
        for tip in seed_tips:
            cursor.execute("""
                INSERT OR IGNORE INTO TipProfiles (id, name, material, color_hex, icon_char, is_default)
                VALUES (?, ?, ?, ?, ?, ?)
            """, tip)

        # Measurements table migration: ensure tip_id exists
        try:
            cursor.execute("ALTER TABLE Measurements ADD COLUMN tip_id INTEGER REFERENCES TipProfiles(id) DEFAULT 1")
        except sqlite3.OperationalError:
            pass

        # Legacy backfill: assign existing measurements to Unbekannt (id=1)
        cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")
```

#### Extended `save_measurement()`:
```python
    def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path="", tip_id=1):
        """Saves a measurement directly as binary numpy arrays for maximum efficiency."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        ml = mag_l.tobytes() if mag_l is not None else b''
        mr = mag_r.tobytes() if mag_r is not None else b''
        pl = phase_l.tobytes() if phase_l is not None else b''
        pr = phase_r.tobytes() if phase_r is not None else b''
        f_bytes = freqs.tobytes() if freqs is not None else b''
        
        actual_tip_id = tip_id if tip_id is not None else 1
        
        cursor.execute("""
            INSERT INTO Measurements 
            (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path, tip_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (iem_id, gain_db, f_bytes, ml, mr, pl, pr, notes, photo_path, actual_tip_id))
              
        conn.commit()
        conn.close()
```

#### New Methods in `DatabaseManager`:
```python
    def get_all_tips(self, include_unknown=True):
        """Returns all ear tips from the catalog as a list of dicts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if include_unknown:
            cursor.execute("SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles ORDER BY id ASC")
        else:
            cursor.execute("SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles WHERE id != 1 ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_last_used_tip(self, iem_id):
        """
        Returns the ID of the most recently used known tip for the specified IEM.
        Excludes 'Unbekannt' (id=1). Returns None if no known tip measurement exists.
        """
        if not iem_id:
            return None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tip_id 
            FROM Measurements 
            WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
        """, (iem_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_reproducibility_scores(self, iem_id, tip_id):
        """
        Computes the reproducibility score (mean standard deviation in dB) band-limited to 20-8000 Hz.
        Scores for Left and Right are strictly separate.
        Returns None if fewer than 5 measurements are available.
        """
        if not iem_id or not tip_id:
            return None
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT frequencies, magnitude_l, magnitude_r
            FROM Measurements
            WHERE iem_id = ? AND tip_id = ?
            ORDER BY timestamp ASC, id ASC
        """, (iem_id, tip_id))
        rows = cursor.fetchall()
        conn.close()
        
        curves_l = []
        curves_r = []
        common_grid = np.geomspace(20.0, 8000.0, 500)
        
        for r in rows:
            f_blob, ml_blob, mr_blob = r[0], r[1], r[2]
            f = np.frombuffer(f_blob, dtype=np.float64) if f_blob else None
            if f is None or len(f) == 0:
                continue
                
            if ml_blob:
                ml = np.frombuffer(ml_blob, dtype=np.float64)
                if len(ml) == len(f):
                    curves_l.append(np.interp(common_grid, f, ml))
                    
            if mr_blob:
                mr = np.frombuffer(mr_blob, dtype=np.float64)
                if len(mr) == len(f):
                    curves_r.append(np.interp(common_grid, f, mr))
                    
        def calc_channel_score(curves):
            n = len(curves)
            if n < 5:
                return None
            mat = np.array(curves)
            # Sample standard deviation across measurements at each frequency bin
            stds = np.std(mat, axis=0, ddof=1)
            mean_std = float(np.mean(stds))
            return {
                "score": round(mean_std, 2),
                "std_dev": round(mean_std, 2),
                "count": n,
                "is_preliminary": bool(5 <= n < 10)
            }
            
        res_l = calc_channel_score(curves_l)
        res_r = calc_channel_score(curves_r)
        
        if res_l is None and res_r is None:
            return None
            
        return {
            "left": res_l,
            "right": res_r
        }

    def get_seal_history(self, iem_id, tip_id):
        """
        Calculates historical acoustic seal (40 Hz vs 500 Hz delta) from stored BLOBs.
        Left and Right are strictly separate.
        """
        if not iem_id or not tip_id:
            return {"left": [], "right": []}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, frequencies, magnitude_l, magnitude_r
            FROM Measurements
            WHERE iem_id = ? AND tip_id = ?
            ORDER BY timestamp ASC, id ASC
        """, (iem_id, tip_id))
        rows = cursor.fetchall()
        conn.close()
        
        history_l = []
        history_r = []
        
        for r in rows:
            meas_id, ts, f_blob, ml_blob, mr_blob = r[0], r[1], r[2], r[3], r[4]
            f = np.frombuffer(f_blob, dtype=np.float64) if f_blob else None
            if f is None or len(f) == 0:
                continue
                
            mask_40 = (f >= 35) & (f <= 45)
            mask_500 = (f >= 450) & (f <= 550)
            if not np.any(mask_40) or not np.any(mask_500):
                continue
                
            if ml_blob:
                ml = np.frombuffer(ml_blob, dtype=np.float64)
                if len(ml) == len(f):
                    val_40 = float(np.mean(ml[mask_40]))
                    val_500 = float(np.mean(ml[mask_500]))
                    delta = val_40 - val_500
                    history_l.append({
                        "id": meas_id,
                        "timestamp": ts,
                        "delta_db": round(delta, 2),
                        "val_40": round(val_40, 2),
                        "val_500": round(val_500, 2),
                        "seal_ok": bool(delta >= -12.0),
                        "status": "OK" if delta >= -12.0 else "LEAK"
                    })
                    
            if mr_blob:
                mr = np.frombuffer(mr_blob, dtype=np.float64)
                if len(mr) == len(f):
                    val_40 = float(np.mean(mr[mask_40]))
                    val_500 = float(np.mean(mr[mask_500]))
                    delta = val_40 - val_500
                    history_r.append({
                        "id": meas_id,
                        "timestamp": ts,
                        "delta_db": round(delta, 2),
                        "val_40": round(val_40, 2),
                        "val_500": round(val_500, 2),
                        "seal_ok": bool(delta >= -12.0),
                        "status": "OK" if delta >= -12.0 else "LEAK"
                    })
                    
        return {
            "left": history_l,
            "right": history_r
        }

    def get_tip_target_peak(self, iem_id, tip_id):
        """
        Extracts tip-specific 8 kHz resonance peak (in 6-10 kHz zone) across stored BLOBs.
        Returns median peak frequency for Left and Right separately.
        """
        if not iem_id or not tip_id:
            return {"left": None, "right": None}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT frequencies, magnitude_l, magnitude_r
            FROM Measurements
            WHERE iem_id = ? AND tip_id = ?
        """, (iem_id, tip_id))
        rows = cursor.fetchall()
        conn.close()
        
        peaks_l = []
        peaks_r = []
        for r in rows:
            f = np.frombuffer(r[0], dtype=np.float64) if r[0] else None
            if f is None: continue
            mask = (f >= 6000) & (f <= 10000)
            if not np.any(mask): continue
            sub_f = f[mask]
            if r[1]:
                ml = np.frombuffer(r[1], dtype=np.float64)
                if len(ml) == len(f):
                    peaks_l.append(float(sub_f[np.argmax(ml[mask])]))
            if r[2]:
                mr = np.frombuffer(r[2], dtype=np.float64)
                if len(mr) == len(f):
                    peaks_r.append(float(sub_f[np.argmax(mr[mask])]))
                    
        return {
            "left": round(float(np.median(peaks_l)), 1) if peaks_l else None,
            "right": round(float(np.median(peaks_r)), 1) if peaks_r else None
        }
```

---

## 5. Verification Method

To verify the planned database schema and config functions independently:

1. **Smoke Test Baseline:**
   Run from repository root:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 smoke_test.py
   ```
   *Expected outcome:* 19/19 checks pass.

2. **Unlock-Gate Unit Test:**
   Execute in Python:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 -c '
   from config import is_prokit_unlocked, unlock_prokit, revoke_prokit
   revoke_prokit()
   assert not is_prokit_unlocked()
   assert not unlock_prokit("INVALID-CODE")
   assert not is_prokit_unlocked()
   assert unlock_prokit("SNITCH-PROKIT-2024-001")
   assert is_prokit_unlocked()
   assert revoke_prokit()
   assert not is_prokit_unlocked()
   print("Unlock unit test: PASSED")
   '
   ```

3. **Database Migration & Seeding Test:**
   Test migration on an isolated temporary database:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 -c '
   import tempfile, os
   from database import DatabaseManager
   with tempfile.TemporaryDirectory() as td:
       db_file = os.path.join(td, "test.db")
       db = DatabaseManager(db_file)
       tips = db.get_all_tips()
       assert len(tips) == 5, f"Expected 5 tips, got {len(tips)}"
       assert tips[0]["id"] == 1 and tips[0]["name"] == "Unbekannt"
       assert db.get_last_used_tip(1) is None
       print("Database migration & seed test: PASSED")
   '
   ```

4. **BLOB Reproducibility & Seal Test:**
   Verify DSP score calculations with synthetic measurements:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 -c '
   import tempfile, os, numpy as np
   from database import DatabaseManager
   with tempfile.TemporaryDirectory() as td:
       db = DatabaseManager(os.path.join(td, "test.db"))
       f = np.linspace(0, 24000, 24001, dtype=np.float64)
       base = 90.0 - (f / 1000.0) * 0.5
       for i in range(7):
           mag = base + np.random.normal(0, 0.2, len(f))
           db.save_measurement(1, f, mag, None, None, None, tip_id=5)
       scores = db.get_reproducibility_scores(1, 5)
       assert scores is not None and scores["left"] is not None
       assert scores["left"]["count"] == 7
       assert scores["left"]["is_preliminary"] == True
       assert scores["right"] is None
       seal = db.get_seal_history(1, 5)
       assert len(seal["left"]) == 7
       assert seal["left"][0]["seal_ok"] == True
       print("BLOB DSP calculations: PASSED")
   '
   ```
