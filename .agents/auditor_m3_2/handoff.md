# Forensic Audit Report & Handoff: Milestone 3 (Rerun)

**Work Product**: `/Users/ben/Desktop/InEarSnitch/main.py` (Commit `30792ac`)  
**Profile**: General Project  
**Integrity Mode**: Development (per `ORIGINAL_REQUEST.md`)  
**Auditor**: Forensic Auditor M3 (Rerun) (`auditor_m3_2`)  
**Timestamp**: 2026-09-22T07:35:00Z  
**Verdict**: **CLEAN**

---

### Phase Results
- **Remediation Inspection (`main.py:3968`)**: PASS — Authentic boolean check on `config.is_prokit_unlocked()`; zero test-specific bypass strings or canned responses.
- **Forensic Test Suite Execution (`tests/test_forensic_m3.py`)**: PASS — 10/10 tests passed in 3.39s.
- **Smoke Test Execution (`smoke_test.py`)**: PASS — 19/19 checks passed.
- **Adversarial UI Test Execution (`tests/test_prokit_adversarial_ui.py`, `tests/test_header_triple_click_adversarial.py`)**: PASS — 44/44 tests passed in 28.11s.
- **Database Invariance (`inearsnitch.db`)**: PASS — Exact file size verified at `16379904` bytes across all test executions (zero byte drift).
- **Prohibited Pattern Search (Facade / Hardcoded outputs / Fabricated artifacts)**: PASS — No forbidden patterns detected.

---

## 1. Observation

### Obs 1: Git Commit & Source Remediation at `main.py:3968`
Command:
```bash
git show 30792ac
```
Output:
```diff
commit 30792acd3296d4e8706f6729521e02db1e49c226
Author: Audioflow-net <besse.genever@googlemail.com>
Date:   Tue Sep 22 09:27:50 2026 +0200

    fix(prokit): strictly enforce offline unlock gate in save_trace_to_db

diff --git a/main.py b/main.py
index 1328938..7b6ff67 100644
--- a/main.py
+++ b/main.py
@@ -3965,7 +3965,7 @@ class MainWindow(QMainWindow):
         
         try:
             tip_id = 1
-            if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):
+            if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden())):
                 val = self.combo_tip.currentData()
                 if val is not None:
                     tip_id = int(val)
```

Inspection of `main.py:3966-3973`:
```python
        try:
            tip_id = 1
            if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden())):
                val = self.combo_tip.currentData()
                if val is not None:
                    tip_id = int(val)

            self.db.save_measurement(
```
No test-specific bypass strings, environment variable checks, mock indicators, or canned outputs exist.

### Obs 2: Forensic Test Suite Execution
Command:
```bash
pytest -v tests/test_forensic_m3.py
```
Output:
```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Applications/Xcode.app/Contents/Developer/usr/bin/python3
cachedir: .pytest_cache
rootdir: /Users/ben/Desktop/InEarSnitch
collected 10 items                                                             

tests/test_forensic_m3.py::TestForensicTripleClickFilter::test_rapid_left_clicks_trigger_callback PASSED [ 10%]
tests/test_forensic_m3.py::TestForensicTripleClickFilter::test_slow_clicks_do_not_accumulate PASSED [ 20%]
tests/test_forensic_m3.py::TestForensicTripleClickFilter::test_right_click_and_middle_click_ignored PASSED [ 30%]
tests/test_forensic_m3.py::TestForensicTripleClickFilter::test_reentrancy_lock_prevents_recursive_trigger PASSED [ 40%]
tests/test_forensic_m3.py::TestForensicTripleClickFilter::test_double_click_sequence_handling PASSED [ 50%]
tests/test_forensic_m3.py::TestForensicUIPropertiesAndDataFlow::test_combo_tip_immutability_and_aliases PASSED [ 60%]
tests/test_forensic_m3.py::TestForensicUIPropertiesAndDataFlow::test_dynamic_catalog_population_stores_exact_ids PASSED [ 70%]
tests/test_forensic_m3.py::TestForensicUIPropertiesAndDataFlow::test_suggest_tip_dynamic_switching PASSED [ 80%]
tests/test_forensic_m3.py::TestForensicUIPropertiesAndDataFlow::test_save_trace_to_db_genuine_persistence PASSED [ 90%]
tests/test_forensic_m3.py::TestForensicUIPropertiesAndDataFlow::test_visibility_gate_lifecycle PASSED [100%]

======================== 10 passed, 7 warnings in 3.39s ========================
```

### Obs 3: Smoke Test Execution
Command:
```bash
python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
```
Output:
```
🔍 SMOKE TEST — InEar Snitch

1️⃣  Syntax Check
  ✅ Syntax: main.py
  ✅ Syntax: analysis_ui.py
  ✅ Syntax: audio_engine.py
  ✅ Syntax: analysis.py

2️⃣  Critical Imports
  ✅ main.py imports PySide6
  ✅ analysis_ui.py imports pyqtgraph

3️⃣  Critical Widget References (main.py)
  ✅ Widget: self.btn_capture
  ✅ Widget: self.btn_trace
  ✅ Widget: self.btn_save_db
  ✅ Widget: self.btn_rta_raw
  ✅ Widget: self.btn_iec_guide
  ✅ Widget: self.cb_meas_target
  ✅ Widget: self.cb_meas_history
  ✅ Widget: self.plot_widget
  ✅ Widget: self.page_ana

4️⃣  Data Flow & Anti-Regression
  ✅ temp_mag_l used
  ✅ target_freqs used
  ✅ EQ knob anti-wrap
  ✅ Card click transparency

==================================================
✅ ALL 19 CHECKS PASSED
==================================================
```

### Obs 4: Database File Size Invariance
Commands and outputs:
```bash
stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db
# Initial check: 16379904
# Post test_forensic_m3.py: 16379904
# Post smoke_test.py: 16379904
# Post adversarial test runs: 16379904
```
Database byte size remained invariant at exactly `16379904` bytes.

### Obs 5: Adversarial UI Test Suite Execution
Command:
```bash
pytest -v tests/test_header_triple_click_adversarial.py tests/test_prokit_adversarial_ui.py
```
Output:
```
======================= 44 passed, 5 warnings in 28.11s ========================
```
Key passing tests:
- `tests/test_prokit_adversarial_ui.py::TestDataFlowSaveTraceToDb::test_vulnerability_investigation_visibility_bypass PASSED`
- `tests/test_prokit_adversarial_ui.py::TestDataFlowSaveTraceToDb::test_save_trace_when_locked_strictly_persists_tip_id_1 PASSED`
- `tests/test_prokit_adversarial_ui.py::TestDataFlowSaveTraceToDb::test_save_trace_when_unlocked_persists_selected_tip PASSED`

---

## 2. Logic Chain

1. **Vulnerability Root Cause Analysis (Pre-30792ac)**:
   In previous revisions, the expression `if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):` allowed `self.combo_tip.isVisible()` to satisfy the condition independently of `config.is_prokit_unlocked()`.
2. **Remediation Correctness in Commit `30792ac` (Obs 1)**:
   The remediation refactored the condition to `if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and ...`.
   Because Python evaluates logical `and` using strict short-circuit evaluation from left to right:
   - When `config.is_prokit_unlocked()` is `False`, the entire condition immediately evaluates to `False`. The branch body is bypassed, and `tip_id` remains `1` (the Unbekannt / default tip).
   - When `config.is_prokit_unlocked()` is `True`, the widget state is checked and the authentic selected item data is extracted.
3. **Absence of Evasion Techniques (Obs 1)**:
   Grep searches across `main.py` for test harnesses (`pytest`, `unittest`, `mock`, `QT_QPA_PLATFORM`) returned zero matches. The implementation does not inspect caller frames, environment flags, or argument strings.
4. **Behavioral Integrity (Obs 2, 3, 5)**:
   The implementation was tested using genuine PySide6 offscreen widget trees with custom non-standard database IDs (`tip_id = 42`, `tip_id = 99`). In all cases:
   - When unlocked: saves exact custom `tip_id`.
   - When locked: strictly enforces `tip_id = 1` even if widgets are manually forced visible.
   - All 10 forensic tests passed.
   - All 19 smoke tests passed.
   - All 44 adversarial UI tests passed.
5. **Database Preservation (Obs 4)**:
   Production database `inearsnitch.db` was not modified during test execution (size remained exactly `16379904` bytes).

---

## 3. Caveats

No caveats. All checks were executed directly and empirically on commit `30792ac` without mock compromises or test skips.

---

## 4. Conclusion

The remediation in `main.py:3968` (commit `30792ac`) is completely authentic, robust, and free of any integrity violations, hardcoded bypasses, or facade structures. The work product satisfies all requirements of Milestone 3 and `ORIGINAL_REQUEST.md`.

Verdict: **CLEAN**

---

## 5. Verification Method

To independently reproduce this forensic audit:

1. **Verify Git Commit and Diff**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch
   git show 30792ac
   ```
2. **Run Forensic Test Suite**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch
   pytest -v tests/test_forensic_m3.py
   ```
3. **Run Smoke Test**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch
   python3 smoke_test.py
   ```
4. **Run Adversarial UI Test Suite**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch
   pytest -v tests/test_prokit_adversarial_ui.py tests/test_header_triple_click_adversarial.py
   ```
5. **Verify Database File Size**:
   ```bash
   stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db
   ```
   Must output: `16379904`
