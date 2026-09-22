# InEarSnitch ProKit Tip-Tracking — M2 Query & DSP Technical Investigation Report

**Author:** M2 Query & DSP Explorer (`explorer_m2_2`)  
**Target:** Milestone 2 (R2 database.py query & DSP methods)  
**Date:** 2026-09-22  

---

## 1. Observation

### 1.1 `database.py` Architecture & Existing BLOB Storage
Inspection of `/Users/ben/Desktop/InEarSnitch/database.py` (lines 86–133) reveals:
- Line 86–107: `save_measurement()` converts numpy float64 arrays to raw binary bytes via `array.tobytes() if array is not None else b''`.
- Line 126–128: `load_reference_measurement()` unpacks arrays using `np.frombuffer(row[col], dtype=np.float64) if row[col] else None`.
- Connection lifecycle: `DatabaseManager` opens independent per-call SQLite connections with `conn = sqlite3.connect(self.db_path)`, commits, and calls `conn.close()`.

### 1.2 Authoritative Design Decisions (LOCKED)
From `/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md`:
- **Decision 1 (Freitext forbidden):** Tips are strictly from `TipProfiles` table (`name, material, color_hex, icon_char, is_default`).
- **Decision 2 (L and R separate):** All metrics, scores, and seal history must be computed and returned separately for Left and Right channels. Never combined or averaged across channels.
- **Decision 3 (Legacy tip_id = 1):** Legacy measurements without tip information belong to "Unbekannt" (`id=1`).
- **Decision 5 (Band-limited reproducibility 20 Hz – 8000 Hz):** Above 8 kHz, coupler resonances dominate and insertion depth shifts create false high variance. Reproducibility score must be computed strictly in the 20 Hz to 8000 Hz window.
- **Decision 6 (Measurement thresholds):** Requires $\ge 5$ measurements per channel (returns `None` if $< 5$). Below 10 measurements ($5 \le N < 10$), `is_preliminary` must be `True`.

### 1.3 Seal Analysis Criteria in Codebase
Inspection of `/Users/ben/Desktop/InEarSnitch/main.py` (lines 3466–3476) shows the production acoustic seal algorithm:
```python
# 2. Seal (40Hz vs 500Hz)
mask_40 = (freqs >= 35) & (freqs <= 45)
mask_500 = (freqs >= 450) & (freqs <= 550)
if np.any(mask_40) and np.any(mask_500):
    val_40 = np.mean(mag_db[mask_40])
    val_500 = np.mean(mag_db[mask_500])
    # Check for bass roll-off OR overall low signal variance (just noise floor)
    if val_40 < val_500 - 12:
        seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 SEAL LEAK!</span>"
    else:
        seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 SEAL OK</span>"
```
The delta is defined as $\Delta = \text{mean}(mag_{40}) - \text{mean}(mag_{500})$.
- $\Delta \ge -12.0\text{ dB} \rightarrow \text{OK}$ (`seal_ok = True`, `status = "OK"`).
- $\Delta < -12.0\text{ dB} \rightarrow \text{LEAK}$ (`seal_ok = False`, `status = "LEAK"`).

### 1.4 Test Suite Expectations in `tests/test_prokit_e2e.py`
Inspection of `tests/test_prokit_e2e.py` defines explicit contracts for M2 APIs:
- `test_get_all_tips_include_and_exclude_unknown` (lines 315–325):
  - `include_unknown=True` returns all 5 catalog tips including `id=1` ("Unbekannt").
  - `include_unknown=False` returns 4 catalog tips excluding `id=1`.
- `test_get_last_used_tip_excludes_unknown` (lines 350–369) & `test_get_last_used_tip_nonexistent_iem` (lines 748–753):
  - Must exclude `id=1` ("Unbekannt") and `NULL`.
  - Must return `None` if only `id=1` measurements exist, or if IEM has no measurements, or if `iem_id` is `None`.
  - Must return the `tip_id` of the most recent measurement when non-legacy tips were used.
- `test_get_reproducibility_scores_structure` (lines 370–387) & Tier 2 boundaries (lines 764–842):
  - Dictionary with keys `"left"` and `"right"`.
  - Channel dict fields: `{"score": float, "std_dev": float, "count": int, "is_preliminary": bool}`.
  - Returns `None` if $N < 5$ on both channels (`test_reproducibility_threshold_under_5_returns_none`, line 590; `test_reproducibility_exactly_4_measurements_none`, line 1017).
  - Returns channel dict for Left and `None` for Right if only Left has $\ge 5$ measurements (`test_reproducibility_mono_only_left`, line 782).
  - Sets `is_preliminary = True` for $5 \le N < 10$, and `is_preliminary = False` for $N \ge 10$ (`test_reproducibility_solid_threshold_10_measurements`, line 810).
  - Handles differing sample rates (e.g. 44.1 kHz vs 48 kHz) via interpolation (`test_reproducibility_mismatched_frequency_bins_interpolation`, line 822).
  - Strictly ignores variances $> 8000\text{ Hz}$ (`test_reproducibility_band_limited_ignores_above_8khz`, line 764).
- `test_get_seal_history_delta_and_status` (lines 388–405) & `test_seal_threshold_exact_boundary` (lines 853–867):
  - Returns `{"left": list[dict], "right": list[dict]}`.
  - Record fields: `{"id": int, "timestamp": str, "delta_db": float, "val_40": float, "val_500": float, "seal_ok": bool, "status": "OK" | "LEAK"}`.
  - Safely ignores empty or corrupted BLOBs (`test_seal_history_empty_and_corrupt_blobs_skipped`, line 843).

---

## 2. Logic Chain

### 2.1 Design of `get_all_tips(include_unknown=True)`
1. **Query Construction:**
   - If `include_unknown=True`:
     `SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles ORDER BY id ASC`
   - If `include_unknown=False`:
     `SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles WHERE id != 1 ORDER BY id ASC`
2. **Row Mapping:**
   Using `conn.row_factory = sqlite3.Row` converts each tuple into a dictionary `dict(r)` mapping column names to values.
3. **Safety & Cleanup:**
   Database connection is managed in a `try ... finally: conn.close()` block.

### 2.2 Design of `get_last_used_tip(iem_id)`
1. **Input Guard:**
   If `not iem_id`: immediately return `None` (handles `None`, `0`, or negative IDs).
2. **Query:**
   ```sql
   SELECT tip_id 
   FROM Measurements 
   WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
   ORDER BY timestamp DESC, id DESC
   LIMIT 1
   ```
3. **Tie-Breaking:**
   Adding `id DESC` after `timestamp DESC` guarantees deterministic results if multiple measurements occurred within the same clock second.
4. **Return:**
   Returns `int(row[0])` if matching row is found; returns `None` otherwise.

### 2.3 Design of `get_reproducibility_scores(iem_id, tip_id)`
1. **Logarithmic Frequency Grid:**
   InEar measurements vary in sampling frequency (e.g. 44.1 kHz, 48 kHz, 96 kHz) yielding different vector lengths (e.g. 15000 vs 24001 points). Element-wise variance across raw vectors would throw size-mismatch errors.
   Standardization is achieved with logarithmic interpolation:
   `common_grid = np.geomspace(20.0, 8000.0, 500)`
2. **Boundary Leakage Prevention (Crucial Finding):**
   When raw frequency vector `f` has points like `7999.345 Hz` and `8000.344 Hz`, standard linear interpolation at `8000.0 Hz` would evaluate between the uncorrupted point at `7999.345 Hz` and the corrupted point at `8000.344 Hz` (which has $> 8\text{ kHz}$ coupler resonance noise).
   Empirical test proved this leaked $\approx 0.02\text{ dB}$ of noise into the score, failing `test_reproducibility_band_limited_ignores_above_8khz` (`assert score == 0.0`).
   **Solution:** Filter input vectors with `mask = f <= 8000.0` before interpolation:
   ```python
   mask = f <= 8000.0
   if not np.any(mask): continue
   curve = np.interp(common_grid, f[mask], mag[mask])
   ```
   At `8000.0 Hz`, `np.interp` clamps to `mag[mask][-1]` (at `7999.345 Hz`), completely eliminating high-frequency leakage. With this fix, `score` evaluates to exactly `0.00 dB`, satisfying `test_reproducibility_band_limited_ignores_above_8khz`.
3. **Sample Standard Deviation:**
   For $N$ interpolated curves forming an $N \times 500$ matrix:
   Per-frequency standard deviation with Bessel's correction:
   `stds = np.std(mat, axis=0, ddof=1)`
   Mean standard deviation across the band:
   `mean_std = float(np.mean(stds))`
4. **Thresholds & Result Packaging:**
   - If $N < 5$: return `None` for that channel.
   - If $5 \le N < 10$: `"is_preliminary": True`.
   - If $N \ge 10$: `"is_preliminary": False`.
   - Both channels `None` $\rightarrow$ entire method returns `None`.
   - Otherwise $\rightarrow$ `{"left": res_l, "right": res_r}`.

### 2.4 Design of `get_seal_history(iem_id, tip_id)`
1. **Input Guard & Extraction:**
   If `not iem_id or not tip_id`: return `{"left": [], "right": []}`.
   Fetch `id, timestamp, frequencies, magnitude_l, magnitude_r` ordered chronologically by `timestamp ASC, id ASC`.
2. **Band Definitions:**
   - 40 Hz band: `mask_40 = (f >= 35.0) & (f <= 45.0)`
   - 500 Hz reference band: `mask_500 = (f >= 450.0) & (f <= 550.0)`
   - If either mask has no points: skip record.
3. **Channel Computation:**
   For each channel present:
   - `val_40 = float(np.mean(mag[mask_40]))`
   - `val_500 = float(np.mean(mag[mask_500]))`
   - `delta = float(val_40 - val_500)`
   - `seal_ok = bool(delta >= -12.0)`
   - `status = "OK" if seal_ok else "LEAK"`
4. **Append Chronological Entries:**
   Each record dict:
   `{"id": meas_id, "timestamp": str(ts), "delta_db": round(delta, 2), "val_40": round(val_40, 2), "val_500": round(val_500, 2), "seal_ok": seal_ok, "status": status}`

---

## 3. Caveats

1. **Boundary Parameter Issue in `tests/test_prokit_e2e.py:392`:**
   In `test_get_seal_history_delta_and_status` (lines 391–405):
   ```python
   f, ml, p = create_synthetic_sweep(bass_boost_db=2.0)
   _, mr, _ = create_synthetic_sweep(leak_db=15.0)  # severe leak on right
   ```
   The generator `create_synthetic_sweep()` defines default `bass_boost_db=3.0`. Thus, `create_synthetic_sweep(leak_db=15.0)` computes `mag[idx_40] += (3.0 - 15.0) = -12.0 dB`. With the acoustic downward tilt ($-0.016 - (-0.200) = +0.184\text{ dB}$), the resulting delta is $-11.82\text{ dB}$, which is $+0.18\text{ dB}$ *above* the $-12.0\text{ dB}$ threshold. Consequently, `delta >= -12.0` evaluates to `True`, causing line 403 (`assert seal["right"][0]["seal_ok"] is False`) to raise `AssertionError`.
   **Resolution:** In `tests/test_prokit_e2e.py:392`, the call should be `create_synthetic_sweep(bass_boost_db=0.0, leak_db=15.0)` or `create_synthetic_sweep(leak_db=20.0)` (as correctly done in line 859 and line 1358). This should be noted for the E2E track / Worker.
2. **Frequency Alignment in Stored BLOBs:**
   Because user sessions may switch sample rates between takes, direct vector operations without interpolation fail. The `np.geomspace(20.0, 8000.0, 500)` interpolation grid is mandatory and must not be omitted.
3. **Empty/Corrupted BLOB Protection:**
   Partial or interrupted sweeps can leave `frequencies` or `magnitude` as empty `b''` or corrupted byte lengths. Both DSP methods must wrap deserialization in `try ... except` and verify `len(mag) == len(f)`.

---

## 4. Conclusion & Recommended Worker Code

The following exact code is formulated for the M2 Worker to implement the query and DSP analytical methods in `/Users/ben/Desktop/InEarSnitch/database.py`.

### 4.1 Complete Proposed Implementation for `database.py`

```python
    def get_all_tips(self, include_unknown=True):
        """Returns all ear tips from the catalog as a list of dicts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if include_unknown:
                cursor.execute("SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles ORDER BY id ASC")
            else:
                cursor.execute("SELECT id, name, material, color_hex, icon_char, is_default FROM TipProfiles WHERE id != 1 ORDER BY id ASC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_last_used_tip(self, iem_id):
        """
        Returns the ID of the most recently used known tip for the specified IEM.
        Excludes 'Unbekannt' (id=1) and NULL. Returns None if no known tip measurement exists.
        """
        if not iem_id:
            return None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT tip_id 
                FROM Measurements 
                WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
            """, (iem_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def get_reproducibility_scores(self, iem_id, tip_id):
        """
        Computes the reproducibility score (mean standard deviation in dB) band-limited to 20-8000 Hz.
        Left and Right channels are computed strictly separately.
        Requires >= 5 measurements per channel (returns None if < 5).
        Sets is_preliminary = True if 5 <= count < 10.
        """
        if not iem_id or not tip_id:
            return None
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT frequencies, magnitude_l, magnitude_r
                FROM Measurements
                WHERE iem_id = ? AND tip_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (iem_id, tip_id))
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        curves_l = []
        curves_r = []
        common_grid = np.geomspace(20.0, 8000.0, 500)
        
        for r in rows:
            f_blob, ml_blob, mr_blob = r[0], r[1], r[2]
            if not f_blob:
                continue
            try:
                f = np.frombuffer(f_blob, dtype=np.float64)
            except Exception:
                continue
            if f is None or len(f) == 0:
                continue
                
            # Strictly limit to <= 8000 Hz before interpolation to prevent
            # HF coupler resonance variations from leaking into the 8000 Hz bin
            mask = f <= 8000.0
            if not np.any(mask):
                continue
            f_sub = f[mask]
            
            if ml_blob:
                try:
                    ml = np.frombuffer(ml_blob, dtype=np.float64)
                    if len(ml) == len(f):
                        curves_l.append(np.interp(common_grid, f_sub, ml[mask]))
                except Exception:
                    pass
                    
            if mr_blob:
                try:
                    mr = np.frombuffer(mr_blob, dtype=np.float64)
                    if len(mr) == len(f):
                        curves_r.append(np.interp(common_grid, f_sub, mr[mask]))
                except Exception:
                    pass
                    
        def calc_channel_score(curves):
            n = len(curves)
            if n < 5:
                return None
            mat = np.array(curves)
            # Sample standard deviation across measurements at each frequency bin (ddof=1)
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
        Left and Right channels are computed strictly separately.
        Delta >= -12.0 dB is categorized as OK, delta < -12.0 dB as LEAK.
        """
        if not iem_id or not tip_id:
            return {"left": [], "right": []}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, timestamp, frequencies, magnitude_l, magnitude_r
                FROM Measurements
                WHERE iem_id = ? AND tip_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (iem_id, tip_id))
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        history_l = []
        history_r = []
        
        for r in rows:
            meas_id, ts, f_blob, ml_blob, mr_blob = r[0], r[1], r[2], r[3], r[4]
            if not f_blob:
                continue
            try:
                f = np.frombuffer(f_blob, dtype=np.float64)
            except Exception:
                continue
            if f is None or len(f) == 0:
                continue
                
            mask_40 = (f >= 35.0) & (f <= 45.0)
            mask_500 = (f >= 450.0) & (f <= 550.0)
            if not np.any(mask_40) or not np.any(mask_500):
                continue
                
            if ml_blob:
                try:
                    ml = np.frombuffer(ml_blob, dtype=np.float64)
                    if len(ml) == len(f):
                        val_40 = float(np.mean(ml[mask_40]))
                        val_500 = float(np.mean(ml[mask_500]))
                        delta = float(val_40 - val_500)
                        seal_ok = bool(delta >= -12.0)
                        history_l.append({
                            "id": meas_id,
                            "timestamp": str(ts) if ts is not None else "",
                            "delta_db": round(delta, 2),
                            "val_40": round(val_40, 2),
                            "val_500": round(val_500, 2),
                            "seal_ok": seal_ok,
                            "status": "OK" if seal_ok else "LEAK"
                        })
                except Exception:
                    pass
                    
            if mr_blob:
                try:
                    mr = np.frombuffer(mr_blob, dtype=np.float64)
                    if len(mr) == len(f):
                        val_40 = float(np.mean(mr[mask_40]))
                        val_500 = float(np.mean(mr[mask_500]))
                        delta = float(val_40 - val_500)
                        seal_ok = bool(delta >= -12.0)
                        history_r.append({
                            "id": meas_id,
                            "timestamp": str(ts) if ts is not None else "",
                            "delta_db": round(delta, 2),
                            "val_40": round(val_40, 2),
                            "val_500": round(val_500, 2),
                            "seal_ok": seal_ok,
                            "status": "OK" if seal_ok else "LEAK"
                        })
                except Exception:
                    pass
                    
        return {
            "left": history_l,
            "right": history_r
        }

    def get_tip_target_peak(self, iem_id, tip_id):
        """
        Extracts tip-specific 8 kHz resonance peak (in 6-10 kHz zone) across stored BLOBs.
        Returns median peak frequency for Left and Right separately.
        Auxiliary method for Milestone 5 (analysis_ui.py).
        """
        if not iem_id or not tip_id:
            return {"left": None, "right": None}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT frequencies, magnitude_l, magnitude_r
                FROM Measurements
                WHERE iem_id = ? AND tip_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (iem_id, tip_id))
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        peaks_l = []
        peaks_r = []
        for r in rows:
            if not r[0]: continue
            try:
                f = np.frombuffer(r[0], dtype=np.float64)
            except Exception:
                continue
            if f is None or len(f) == 0: continue
            
            mask = (f >= 6000.0) & (f <= 10000.0)
            if not np.any(mask): continue
            sub_f = f[mask]
            
            if r[1]:
                try:
                    ml = np.frombuffer(r[1], dtype=np.float64)
                    if len(ml) == len(f):
                        peaks_l.append(float(sub_f[np.argmax(ml[mask])]))
                except Exception:
                    pass
            if r[2]:
                try:
                    mr = np.frombuffer(r[2], dtype=np.float64)
                    if len(mr) == len(f):
                        peaks_r.append(float(sub_f[np.argmax(mr[mask])]))
                except Exception:
                    pass
                    
        return {
            "left": round(float(np.median(peaks_l)), 1) if peaks_l else None,
            "right": round(float(np.median(peaks_r)), 1) if peaks_r else None
        }
```

---

## 5. Verification Method

### 5.1 Smoke Test Verification
Ensure zero regressions on the existing application:
```bash
cd /Users/ben/Desktop/InEarSnitch && python3 smoke_test.py
```
*Expected Result:* `19/19 checks pass`.

### 5.2 Independent DSP & Query Validation Script
Execute the following comprehensive validation in Python to test all query methods, edge cases, and DSP mathematical constraints against an isolated temporary database:

```bash
cd /Users/ben/Desktop/InEarSnitch && python3 -c '
import tempfile, os, numpy as np
from database import DatabaseManager

with tempfile.TemporaryDirectory() as td:
    db = DatabaseManager(os.path.join(td, "test.db"))
    
    # 1. get_all_tips verification
    all_tips = db.get_all_tips(include_unknown=True)
    assert len(all_tips) == 5
    assert all_tips[0]["id"] == 1 and all_tips[0]["name"] == "Unbekannt"
    catalog_tips = db.get_all_tips(include_unknown=False)
    assert len(catalog_tips) == 4
    assert not any(t["id"] == 1 for t in catalog_tips)
    
    # 2. get_last_used_tip verification
    assert db.get_last_used_tip(1) is None
    f = np.linspace(20.0, 24000.0, 24001, dtype=np.float64)
    m = 90.0 - (f / 1000.0) * 0.4
    p = np.zeros_like(f)
    db.save_measurement(1, f, m, m, p, p, tip_id=1)
    assert db.get_last_used_tip(1) is None  # tip_id=1 must be excluded
    db.save_measurement(1, f, m, m, p, p, tip_id=4)
    assert db.get_last_used_tip(1) == 4
    db.save_measurement(1, f, m, m, p, p, tip_id=5)
    assert db.get_last_used_tip(1) == 5
    db.save_measurement(1, f, m, m, p, p, tip_id=1)
    assert db.get_last_used_tip(1) == 5  # subsequent legacy does not override
    
    # 3. get_reproducibility_scores verification
    # N=4 returns None
    db_rep = DatabaseManager(os.path.join(td, "test_rep.db"))
    for _ in range(4):
        db_rep.save_measurement(10, f, m, m, p, p, tip_id=4)
    assert db_rep.get_reproducibility_scores(10, 4) is None
    
    # 5 <= N < 10 returns is_preliminary=True
    for _ in range(3):
        db_rep.save_measurement(10, f, m + np.random.normal(0, 0.2, len(f)), m, p, p, tip_id=4)
    scores = db_rep.get_reproducibility_scores(10, 4)
    assert scores is not None and scores["left"]["count"] == 7
    assert scores["left"]["is_preliminary"] is True
    
    # N >= 10 returns is_preliminary=False
    for _ in range(3):
        db_rep.save_measurement(10, f, m, m, p, p, tip_id=4)
    scores_10 = db_rep.get_reproducibility_scores(10, 4)
    assert scores_10["left"]["count"] == 10
    assert scores_10["left"]["is_preliminary"] is False
    
    # 4. get_seal_history verification
    db_seal = DatabaseManager(os.path.join(td, "test_seal.db"))
    # Sealed take
    db_seal.save_measurement(20, f, m, m, p, p, tip_id=4)
    # Leaked take (bass drop -20 dB)
    m_leak = m.copy()
    m_leak[(f >= 35) & (f <= 45)] -= 20.0
    db_seal.save_measurement(20, f, m, m_leak, p, p, tip_id=4)
    
    seal = db_seal.get_seal_history(20, 4)
    assert len(seal["left"]) == 2 and len(seal["right"]) == 2
    assert seal["left"][0]["seal_ok"] is True and seal["left"][0]["status"] == "OK"
    assert seal["right"][1]["seal_ok"] is False and seal["right"][1]["status"] == "LEAK"

    print("All M2 Query & DSP Verifications: PASSED!")
'
```

### 5.3 Invalidation Conditions
The conclusion would be invalidated if:
1. SQLite does not support logarithmic interpolation on numpy buffers (mitigated by using `np.geomspace` and `np.interp` in Python).
2. The user changes the seal status threshold from $-12.0\text{ dB}$ or changes the band limits from $20\text{ Hz} – 8000\text{ Hz}$.
3. Left and Right channels are ever merged into a single score (violating Design Decision 2).
