# M4 Forensic Integrity Audit Report: Milestone 4 (R4 history_ui.py)

**Work Product**: `/Users/ben/Desktop/InEarSnitch/history_ui.py`  
**Profile**: General Project (Development Mode)  
**Verdict**: **CLEAN**  

---

## Forensic Audit Summary

| Check | Focus Area | Result | Details |
|---|---|:---:|---|
| **1. Static Code Analysis** | Vector math authenticity in `HistoryCardWidget.compute_seal_for_channel` | **PASS** | Genuine NumPy vector slicing on bands 35–45 Hz and 450–550 Hz; delta computed as `mean(35-45Hz) - mean(450-550Hz)` against threshold `-11.8 dB`. No canned or hardcoded numbers. |
| **2. SQL Query Authenticity** | Database querying in `HistoryWidget.load_history()` | **PASS** | Authentic `LEFT JOIN TipProfiles t ON m.tip_id = t.id` with fallback `COALESCE(m.tip_id, 1)` and `COALESCE(t.name, 'Unbekannt')`. |
| **3. Anti-Cheating Scan** | Test-detection branching & dummy facades | **PASS** | Zero instances of `pytest`, `test_`, `mock`, or environment variable sniffers in `history_ui.py`. Real PySide6 widgets instantiated and populated from real SQLite rows. |
| **4. Live Database Invariance** | Production DB integrity (`inearsnitch.db`) | **PASS** | File size is exactly **16,379,904** bytes. Live database contains exactly 9 pre-existing user records (from Sep 1–13, 2026). Zero synthetic test records or corrupted entries written. |
| **5. Runtime Math & Edge Cases** | Dynamic execution & stress testing | **PASS** | Dynamic tests on arbitrary vectors accurately calculate seal status for OK, LEAK, boundary (-11.8 dB vs -11.9 dB), and cleanly handle invalid/empty data. |
| **6. Smoke & E2E Test Suite** | Anti-regression & test suite pass | **PASS** | `smoke_test.py` passes 19/19 checks. All 17 E2E tests covering History UI and seal metrics in `test_prokit_e2e.py` pass cleanly. |

---

## 1. Observation

1. **Static Analysis of `HistoryCardWidget.compute_seal_for_channel` (`history_ui.py:54-80`)**:
   ```python
   @staticmethod
   def compute_seal_for_channel(freq, mag):
       if freq is None or mag is None:
           return None, None
       try:
           if len(freq) < 10 or len(mag) != len(freq):
               return None, None
           mask_40 = (freq >= 35.0) & (freq <= 45.0)
           mask_500 = (freq >= 450.0) & (freq <= 550.0)
           if not np.any(mask_40) or not np.any(mask_500):
               return None, None
           val_40 = float(np.mean(mag[mask_40]))
           val_500 = float(np.mean(mag[mask_500]))
           delta = val_40 - val_500
           delta_db = float(round(delta, 1))
           status = "OK" if delta_db >= HistoryCardWidget.SEAL_THRESHOLD_DB else "LEAK"
           return status, delta_db
       except Exception:
           return None, None
   ```
   Threshold is defined on line 52 as `SEAL_THRESHOLD_DB = -11.8`.

2. **SQL Query in `load_history()` (`history_ui.py:718-720`)**:
   ```python
   cursor.execute('''
       SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name, m.meas_name, COALESCE(m.tip_id, 1) AS tip_id, COALESCE(t.name, 'Unbekannt') AS tip_name, COALESCE(t.icon_char, '?') AS tip_icon, COALESCE(t.color_hex, '#6b7280') AS tip_color FROM Measurements m JOIN IEM_Models iem ON m.iem_id = iem.id LEFT JOIN TipProfiles t ON m.tip_id = t.id WHERE iem.musician_id = ? ORDER BY m.timestamp DESC LIMIT 100
   ''', (m_id,))
   ```

3. **Absence of Test-Sniffing / Cheating Constructs**:
   - `grep_search` across `history_ui.py` for `pytest`: 0 matches.
   - `grep_search` across `history_ui.py` for `test_`: 0 matches.
   - `grep_search` across `history_ui.py` for `environ`: 0 matches.

4. **Live Production Database Forensics (`inearsnitch.db`)**:
   - Size check via `ls -l /Users/ben/Desktop/InEarSnitch/inearsnitch.db`:
     `-rw-r--r--@ 1 ben staff 16379904 Sep 22 09:22 /Users/ben/Desktop/InEarSnitch/inearsnitch.db`
     (Matches required 16,379,904 bytes exactly).
   - Record contents query:
     - Total `Measurements`: 9 (IDs: 1, 2, 3, 4, 5, 6, 24, 25, 26). All dated between 2026-09-01 and 2026-09-13.
     - Total rows with test/synthetic notes or names: 0.
     - Total rows with `tip_id IS NULL`: 0.
     - `TipProfiles` table: 5 rows (1: 'Unbekannt', 2: 'Kein Aufsatz', 3: 'Standard Foam', 4: 'ProKit V1', 5: 'ProKit V2').

5. **Runtime Verification**:
   - Dynamic math check executed on synthesized vectors:
     - Good seal (delta -5.0 dB): returned `('OK', -5.0)`.
     - Leak seal (delta -15.0 dB): returned `('LEAK', -15.0)`.
     - Exact threshold (delta -11.8 dB): returned `('OK', -11.8)`.
     - Below threshold (delta -11.9 dB): returned `('LEAK', -11.9)`.
     - Length mismatch / missing frequencies: returned `(None, None)`.
   - Dynamic widget verification:
     - Unknown tip (`tip_id=1`): displayed "?" on `#6b7280` background.
     - Custom tip (`tip_id=4`): displayed "◆ ProKit V1" on `#3b82f6` background.
     - ProKit locked: badge and seal widgets hidden (`isHidden() == True`).
     - ProKit unlocked: badge and seal widgets visible (`isHidden() == False`).
     - Dynamic query and card population in `HistoryWidget.load_history()` with temporary SQLite database passed all assertions.

6. **Automated Test Results**:
   - `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`: 19/19 checks PASSED.
   - `pytest -v tests/test_prokit_e2e.py -k "History or Hist or badge or seal"`: 17/17 tests PASSED.

---

## 2. Logic Chain

1. **From Observation 1**: The implementation of `HistoryCardWidget.compute_seal_for_channel` accepts raw NumPy arrays, isolates frequencies in [35.0, 45.0] Hz and [450.0, 550.0] Hz, calculates arithmetic means `val_40` and `val_500`, rounds the difference to 1 decimal place, and evaluates against `-11.8 dB`. Therefore, acoustic seal computation is genuine, scientifically sound, and non-canned.
2. **From Observation 2**: `HistoryWidget.load_history()` constructs an authentic SQL query with `LEFT JOIN TipProfiles t ON m.tip_id = t.id`. It extracts the actual tip attributes (`tip_name`, `tip_icon`, `tip_color`) and stores them in the card item data, fulfilling Requirement R4.
3. **From Observation 3**: No conditional branches inspect caller frames, `pytest`, or test environment flags. The implementation operates identically under production and test runners.
4. **From Observation 4**: The file size of `/Users/ben/Desktop/InEarSnitch/inearsnitch.db` is 16,379,904 bytes. No synthetic test traces or corrupted records exist. Invariance has been preserved.
5. **From Observations 5 & 6**: Dynamic execution with offscreen PySide6 confirms that the UI and DSP math behave predictably and correctly across all boundary conditions without regressions.

---

## 3. Caveats

- Milestone 5 (`analysis_ui.py`) is not yet implemented (scheduled for subsequent milestone). The single failing test in `test_prokit_e2e.py` (`test_helmholtz_peak_detection_algorithm`) pertains exclusively to M5 resonance peak detection and has zero bearing on M4 (`history_ui.py`).
- No other caveats.

---

## 4. Conclusion

Milestone 4 (R4 `history_ui.py`) satisfies all forensic integrity criteria without violation. The code is genuine, properly architected, resilient against edge cases, adheres to the locked design decisions (L and R separate, catalog-only tips, Unbekannt fallback), and does not modify or contaminate the live database.

**Verdict: CLEAN**

---

## 5. Verification Method

To independently verify this audit, run:

1. **Verify Database Invariance**:
   ```bash
   ls -l /Users/ben/Desktop/InEarSnitch/inearsnitch.db
   # Expected size: 16379904 bytes
   ```

2. **Verify Smoke Test**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   # Expected: ALL 19 CHECKS PASSED
   ```

3. **Run M4 E2E Test Suite**:
   ```bash
   pytest -v /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py -k "History or Hist or badge or seal"
   # Expected: 17 passed, 70 deselected
   ```

4. **Verify Absence of Test Detection**:
   ```bash
   grep -En "(pytest|test_|is_test)" /Users/ben/Desktop/InEarSnitch/history_ui.py
   # Expected: No output
   ```
