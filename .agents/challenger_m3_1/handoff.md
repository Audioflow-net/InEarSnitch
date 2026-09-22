# Handoff Report: M3 Adversarial Challenge — UI Selector, Dynamic Visibility & Data Flow

**Agent**: M3 Adversarial Challenger 1 (`challenger_m3_1`)  
**Timestamp**: 2026-09-22T07:25:00Z  
**Verdict**: **REQUEST_CHANGES**  

---

## 1. Observation

### Obs 1: ComboBox Non-Editability & Input Resistance (`main.py:1237-1242`)
In `/Users/ben/Desktop/InEarSnitch/main.py`:
```python
1237:         self.combo_tip = QComboBox()
1238:         self.combo_tip.setObjectName("cb_prokit_tip")
1239:         self.combo_tip.setEditable(False)
1240:         self.combo_tip.setFixedWidth(135)
1241:         self.combo_tip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
1242:         self.combo_tip.setToolTip("Select ProKit Coupler Ear Tip")
```
- Direct execution verified: `self.combo_tip.isEditable() is False`.
- `self.combo_tip.lineEdit() is None`.
- Injected `QKeyEvent` sequences with arbitrary strings (`"Custom Tip"`, `"<script>alert(1)</script>"`, `"' OR 1=1--"`, `"A"*1000`) produced no new items or modifications to catalog items.
- Item count strictly matches database catalog (5 items, seed IDs `[1, 2, 3, 4, 5]`).

### Obs 2: Dynamic Visibility Lifecycle (`main.py:1276-1277, 4084-4108`)
In `/Users/ben/Desktop/InEarSnitch/main.py`:
```python
1276:         self.populate_tips()
1277:         self.tip_container.setVisible(config.is_prokit_unlocked())
...
4084:     def update_prokit_ui_visibility(self):
4085:         """Update visibility of ProKit UI controls based on unlock state."""
4086:         unlocked = config.is_prokit_unlocked()
4087:         if hasattr(self, 'tip_container'):
4088:             self.tip_container.setVisible(unlocked)
4089:         if hasattr(self, 'combo_tip'):
4090:             self.combo_tip.setVisible(unlocked)
```
- Initial startup state (locked): `win.tip_container.isHidden() is True`, `win.combo_tip.isHidden() is True`.
- Following `config.unlock_prokit(...)` + `update_prokit_ui_visibility()`: `win.tip_container.isHidden() is False`, `win.combo_tip.isHidden() is False`.
- Following `config.revoke_prokit()` + `update_prokit_ui_visibility()`: `win.tip_container.isHidden() is True`, `win.combo_tip.isHidden() is True`.
- 50 rapid alternating unlock/revoke toggles executed cleanly with no desynchronization.

### Obs 3: EMPIRICAL VULNERABILITY — ProKit Gate Bypass in `save_trace_to_db` (`main.py:3967-3972`)
In `/Users/ben/Desktop/InEarSnitch/main.py`:
```python
3967:             tip_id = 1
3968:             if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):
3969:                 val = self.combo_tip.currentData()
3970:                 if val is not None:
3971:                     tip_id = int(val)
```
- **Operator Precedence / Grouping Flaw**:
  Notice the boolean condition: `(self.combo_tip.isVisible() or (hasattr(...) and not self.tip_container.isHidden() and config.is_prokit_unlocked()))`.
  The left operand of `or` is `self.combo_tip.isVisible()`, which **does not check `config.is_prokit_unlocked()`**.
- **Empirical Proof of Vulnerability**:
  Running the following test in offscreen Qt:
  ```python
  win = MainWindow()
  win.show()
  assert config.is_prokit_unlocked() is False
  win.tip_container.show()
  win.combo_tip.show()
  win.current_iem_id = 1
  win.combo_tip.setCurrentIndex(win.combo_tip.findData(4))
  win.save_trace_to_db()
  ```
  Result:
  `EMPIRICAL RESULT: ProKit unlocked = False, combo_tip.isVisible() = True, persisted tip_id = 4`
- **Impact**: While ProKit is locked (`config.is_prokit_unlocked() is False`), if `combo_tip` is visible (e.g. through widget hierarchy changes, theme reloading, layout reparenting, or UI exposure), `save_trace_to_db` fails to enforce the lock and persists `tip_id = 4` to the database instead of `1`.

### Obs 4: Multi-IEM Profile Switching & Auto-Suggestion (`main.py:3034-3035, 4139-4165`)
In `/Users/ben/Desktop/InEarSnitch/main.py`:
```python
4139:     def suggest_tip_for_current_iem(self):
4140:         """Auto-suggest last used tip for current IEM, falling back to default."""
4141:         if not hasattr(self, 'combo_tip') or not hasattr(self, 'db'):
4142:             return
4143:         
4144:         last_tip_id = None
4145:         if getattr(self, 'current_iem_id', None) and hasattr(self.db, 'get_last_used_tip'):
4146:             try:
4147:                 last_tip_id = self.db.get_last_used_tip(self.current_iem_id)
4148:             except Exception:
4149:                 last_tip_id = None
4150:             
4151:         if last_tip_id is not None:
4152:             idx = self.combo_tip.findData(last_tip_id)
4153:             if idx != -1:
4154:                 self.combo_tip.setCurrentIndex(idx)
4155:                 return
4156:                 
4157:         # Fallback to default tip (is_default == 1, id=5)
4158:         def_idx = self.combo_tip.findData(5)
4159:         if def_idx != -1:
4160:             self.combo_tip.setCurrentIndex(def_idx)
4161:         elif self.combo_tip.count() > 0:
4162:             self.combo_tip.setCurrentIndex(0)
```
- Tested 5 distinct IEM profiles:
  - IEM 1 (last tip = 2) -> `combo_tip.currentData() == 2`
  - IEM 2 (last tip = 3) -> `combo_tip.currentData() == 3`
  - IEM 3 (last tip = 4) -> `combo_tip.currentData() == 4`
  - IEM 4 (last tip = 5) -> `combo_tip.currentData() == 5`
  - IEM 5 (only legacy measurements with tip_id=1) -> `combo_tip.currentData() == 5` (proper fallback)
- Forward and reverse switching order both pass.
- IEM with 0 measurements properly falls back to `tip_id=5`.
- Active measurement lock (`is_measuring = True`) cleanly blocks profile switching.

### Obs 5: Test Execution Results
- `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`: Passed (19/19 checks).
- `pytest -v tests/test_prokit_adversarial_ui.py`: All 21 tests passed.
- `pytest -v tests/test_prokit_e2e.py`: 86 passed, 1 failed (`TestTier1DiagnosticsCard::test_helmholtz_peak_detection_algorithm`, belonging to M5 scope).

---

## 2. Logic Chain

1. **Safety Contract**:
   Design Decision #3 and Acceptance Criteria dictate:
   *"When ProKit is locked, is tip_container hidden, and does save_trace_to_db strictly persist tip_id=1?"*
2. **Implementation Defect**:
   In `main.py:3968`, the expression is:
   `if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):`
3. **Causality**:
   Because `self.combo_tip.isVisible()` is OR'd with the conjunct containing `config.is_prokit_unlocked()`, truthiness of `self.combo_tip.isVisible()` short-circuits the evaluation and completely skips checking whether ProKit is unlocked.
4. **Empirical Verification**:
   When `win.show()` and `combo_tip.show()` were active while `config.is_prokit_unlocked() is False`, `save_trace_to_db` wrote `tip_id = 4` into the `Measurements` table.
5. **Deduction**:
   Under adversarial conditions, the offline unlock gate is bypassed in `save_trace_to_db`. To strictly enforce `tip_id=1` when locked, `config.is_prokit_unlocked()` must be the mandatory outer condition.

---

## 3. Caveats

- Under standard, non-adversarial user flow, `self.tip_container.setVisible(False)` ensures `self.combo_tip.isVisible()` evaluates to `False`, so normal users running the app without UI tampering will persist `tip_id = 1` while locked.
- However, as empirical challengers, our mandate is to identify failure modes and boundary vulnerabilities. Gating persistence on UI visibility rather than cryptographic unlock state is a structural flaw.
- All tests were executed on temporary SQLite databases (`tempfile.TemporaryDirectory`); production database `inearsnitch.db` was untouched.

---

## 4. Conclusion & Required Changes

**Verdict: REQUEST_CHANGES**

### Required Change in `main.py` (line 3968)
Modify `save_trace_to_db` to enforce `config.is_prokit_unlocked()` as a mandatory top-level condition:

**Current (`main.py:3968`)**:
```python
if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):
    val = self.combo_tip.currentData()
    if val is not None:
        tip_id = int(val)
```

**Required Fix**:
```python
if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden())):
    val = self.combo_tip.currentData()
    if val is not None:
        tip_id = int(val)
```

This single-line fix guarantees that `tip_id` can NEVER be persisted as anything other than 1 while ProKit is locked, regardless of UI rendering state or widget visibility anomalies.

---

## 5. Verification Method

### Command to Run Smoke Test
```bash
python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
```

### Command to Run Adversarial UI Suite
```bash
python3 -m pytest -v /Users/ben/Desktop/InEarSnitch/tests/test_prokit_adversarial_ui.py
```

### Command to Reproduce Visibility Bypass Vulnerability
```bash
python3 -c '
import os, sys, tempfile, numpy as np, sqlite3
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from unittest.mock import patch

with tempfile.TemporaryDirectory() as td:
    temp_db = os.path.join(td, "test.db")
    import config, database
    with patch("config.get_data_dir", return_value=td), \
         patch("database.DatabaseManager.__init__", lambda self, db_path=temp_db: database.DatabaseManager.__dict__["_init_db"](setattr(self, "db_path", db_path) or self)):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        from main import MainWindow
        with patch.object(MainWindow, "check_eula", lambda self: None):
            win = MainWindow()
            win.show()
            assert config.is_prokit_unlocked() is False
            win.tip_container.show()
            win.combo_tip.show()
            win.current_iem_id = 1
            win.temp_freqs = np.linspace(20, 20000, 1000)
            win.temp_mag_l = np.ones(1000) * 85.0
            win.temp_mag_r = np.ones(1000) * 85.0
            win.temp_phase_l = np.zeros(1000)
            win.temp_phase_r = np.zeros(1000)
            win.combo_tip.setCurrentIndex(win.combo_tip.findData(4))
            win.save_trace_to_db()

            conn = sqlite3.connect(temp_db)
            cur = conn.cursor()
            cur.execute("SELECT tip_id FROM Measurements ORDER BY id DESC LIMIT 1")
            saved_tip = cur.fetchone()[0]
            print(f"Persisted tip_id while locked: {saved_tip}")
            assert saved_tip == 1, f"VULNERABILITY CONFIRMED: Expected 1, got {saved_tip}"
            conn.close()
'
```
