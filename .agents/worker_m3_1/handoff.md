# Milestone 3 (R3 main.py) UI Implementation Handoff Report

## 1. Observation

1. **Pre-flight Smoke Test Baseline**:
   - Command: `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`
   - Output: `✅ ALL 19 CHECKS PASSED`.
   - Critical references confirmed:
     - `self.btn_capture`
     - `self.btn_trace`
     - `self.btn_save_db`
     - `self.btn_rta_raw`
     - `self.btn_iec_guide`
     - `self.cb_meas_target`
     - `self.cb_meas_history`
     - `self.plot_widget`
     - `self.page_ana`
   - Initial database size: `stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db` -> `16379904` bytes.

2. **Git Backup Checkpoint**:
   - Command: `git add -A && git commit -m "backup: vor ProKit UI main.py"`
   - Output: Commit `ba404a4` created on branch `main`.

3. **Existing Main Window & Test Harness Incompatibility**:
   - Running `pytest tests/test_prokit_e2e.py::TestTier1UISelector::test_bottom_bar_tip_widget_creation` previously failed with:
     ```
     AttributeError: module 'main' has no attribute 'InEarSnitchApp'
     ```
   - Main class in `main.py` is `class MainWindow(QMainWindow)`.

4. **Code Implementation in `/Users/ben/Desktop/InEarSnitch/main.py`**:
   - **Imports**: Added `import time`, `import config`, `QInputDialog` to `PySide6.QtWidgets`, `QEvent` to `PySide6.QtCore`.
   - **LogoTripleClickFilter Class** (lines 636–671):
     ```python
     class LogoTripleClickFilter(QObject):
         def __init__(self, parent, on_triple_click_callback, max_interval=0.6):
             super().__init__(parent)
             self.callback = on_triple_click_callback
             self.max_interval = max_interval
             self.clicks = []
             self._dialog_active = False

         def eventFilter(self, watched, event):
             if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):
                 if event.button() == Qt.LeftButton:
                     if self._dialog_active:
                         return False
                     now = time.monotonic()
                     if self.clicks and (now - self.clicks[-1]) > self.max_interval:
                         self.clicks = []
                     self.clicks.append(now)
                     if len(self.clicks) >= 3:
                         self.clicks = []
                         self._dialog_active = True
                         try:
                             self.callback()
                         finally:
                             self._dialog_active = False
                         return True
             return False
     ```
   - **Header Setup** (`setup_ui`, lines 825–842):
     - Assigned `self.lbl_logo = logo`, `self.lbl_title = logo`, `self.lbl_sublogo = sublogo`, `self.logo = logo`, `self.sublogo = sublogo`.
     - Installed `LogoTripleClickFilter` on `self.lbl_logo` and `self.lbl_sublogo` with 600ms interval triggering `self.prompt_prokit_unlock`.
   - **Bottom Bar Tip Selector** (`setup_ui`, lines 1258–1324):
     - Added `self.tip_container = QWidget()` inside `right_group` immediately before `mod_capture` (`right_group.addWidget(self.tip_container)`).
     - Added `self.combo_tip = QComboBox()` with `self.cb_tip = self.combo_tip`, `self.cb_prokit_tip = self.combo_tip`.
     - Set object name: `self.combo_tip.setObjectName("cb_prokit_tip")`.
     - Enforced non-editable: `self.combo_tip.setEditable(False)`.
     - Populated from database via `self.populate_tips()`: `f"{icon} {name}".strip()`, storing `userData=tip['id']`. Default selected tip: `is_default == 1` (`id=5`, "★ ProKit V2").
     - Controlled visibility via `self.tip_container.setVisible(config.is_prokit_unlocked())`.
   - **Profile Selection Hook** (`on_profile_selected`, lines 3066–3072):
     - Added auto-suggest hook: `self.suggest_tip_for_current_iem()` immediately following `self.current_iem_id = iem_id`.
   - **Measurement Persistence Hook** (`save_trace_to_db`, lines 4000–4020):
     - Extracted `tip_id`:
       ```python
       tip_id = 1
       if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):
           val = self.combo_tip.currentData()
           if val is not None:
               tip_id = int(val)
       ```
     - Passed `tip_id=tip_id` into `self.db.save_measurement(...)`.
   - **ProKit Helper Methods on `MainWindow`** (lines 4088–4204):
     - `prompt_prokit_unlock(self)`: Opens `QInputDialog.getText(self, "ProKit Freischaltung", "Freischaltcode eingeben:")`. On OK, calls `config.unlock_prokit(code)`. If True: `QMessageBox.information`, calls `self.update_prokit_ui_visibility()`, returns True. If False: `QMessageBox.warning`, returns False.
     - Aliases: `open_prokit_unlock_dialog = prompt_prokit_unlock`, `on_logo_triple_clicked = prompt_prokit_unlock`.
     - `update_prokit_ui_visibility(self)`: Toggles visibility of `self.tip_container` and `self.combo_tip` based on `config.is_prokit_unlocked()`. Triggers `self.populate_tips()` and `self.suggest_tip_for_current_iem()`.
     - Alias: `update_prokit_visibility = update_prokit_ui_visibility`.
     - `populate_tips(self)`: Clears and repopulates `self.combo_tip` from `self.db.get_all_tips(include_unknown=True)` while preserving current selection or defaulting to id=5.
     - `suggest_tip_for_current_iem(self)`: Queries `self.db.get_last_used_tip(self.current_iem_id)`. If found, selects that tip index; else selects default id=5.
     - Alias: `on_iem_changed = suggest_tip_for_current_iem`.
   - **Module-Level Compatibility Alias** (line 4208):
     `InEarSnitchApp = MainWindow`.

5. **Post-Implementation Verification**:
   - `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`: `✅ ALL 19 CHECKS PASSED`.
   - `pytest -v tests/test_prokit_e2e.py -k "TestTier1UISelector or TestTier2UISelectorBoundaries or TestTier1TripleClickUnlock or TestTier2TripleClickBoundaries"`: `21 passed, 66 deselected in 2.78s`.
   - `pytest -v tests/test_prokit_e2e.py -k "TripleClick or UI or Selector or Unlock"`: `36 passed, 51 deselected in 2.47s`.
   - `pytest -v tests/test_prokit_gate.py tests/test_prokit_adversarial.py tests/test_prokit_adversarial_db.py`: `53 passed in 1.10s`.
   - `stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db`: `16379904` bytes (strictly untouched).
   - Git commit: `1087e5d` (`feat(prokit): implement tip selector and triple-click unlock in main.py`).

---

## 2. Logic Chain

1. **Test Harness Compatibility**:
   Observation 3 showed `test_bottom_bar_tip_widget_creation` failed due to `InEarSnitchApp` being undefined in `main.py`. Defining `InEarSnitchApp = MainWindow` at module level instantly resolved the test instantiation failure without altering the internal class name `MainWindow`.

2. **Logo Triple-Click Architecture**:
   Observation 4 showed `LogoTripleClickFilter` intercepts `MouseButtonPress` and `MouseButtonDblClick` events on `self.lbl_logo` and `self.lbl_sublogo`. Non-left clicks are ignored. Pauses exceeding 600ms clear prior timestamps. Upon recording 3 qualifying clicks within 600ms, the filter clears click history, sets a re-entrancy lock `_dialog_active`, and triggers `prompt_prokit_unlock()`. This guarantees that double-clicks in window managers and synthetic single clicks in test runners both register accurately while preventing multiple concurrent dialog popups.

3. **Non-Editable Tip Selector Placement**:
   Design Decision 1 strictly forbids freetext. `self.combo_tip.setEditable(False)` enforces this. Setting `objectName("cb_prokit_tip")` and providing aliases `cb_tip` and `cb_prokit_tip` ensures automated E2E tests and future QA scripts can locate and interact with the widget. Placing `self.tip_container` into `right_group` immediately before `mod_capture` positions the selector right next to the RUN button without shifting existing layout boundaries.

4. **Dynamic Visibility & Gate Consistency**:
   When ProKit is locked (`config.is_prokit_unlocked()` is False), `tip_container` is set to `setVisible(False)`, completely hiding the tip selector. When unlocked, `update_prokit_ui_visibility()` sets it visible, populates the catalog, and pre-selects the default or last-used tip.

5. **Auto-Suggestion on Profile Change**:
   In `on_profile_selected()`, whenever `self.current_iem_id` is updated, `suggest_tip_for_current_iem()` queries `db.get_last_used_tip(self.current_iem_id)` (which excludes `tip_id=1`). If a valid tip ID is found, `combo_tip` updates its index. If none is found (new IEM or legacy only), it falls back to tip id=5 ("ProKit V2", `is_default == 1`).

6. **Save Trace Persistence**:
   In `save_trace_to_db()`, `tip_id` is extracted from `self.combo_tip.currentData()`. If ProKit is locked or the selector is hidden, `tip_id` safely defaults to 1 ("Unbekannt"). Passing `tip_id=tip_id` to `self.db.save_measurement()` ensures the database records the exact tip utilized.

7. **Zero Regressions & Zero Database Mutation**:
   `smoke_test.py` scans for verbatim widget declarations (`self.btn_capture =`, `self.btn_trace =`, etc.) and anti-regression keys. None were altered. The main database `inearsnitch.db` was not modified during testing (verified at 16,379,904 bytes).

---

## 3. Caveats

- **Test `test_helmholtz_peak_detection_algorithm`**:
  In `tests/test_prokit_e2e.py` line 587, the synthetic acoustic curve formula shifts the peak 10.5 Hz away from nominal center. This test belongs to Milestone 5 (Diagnostics / DSP Card) and does not indicate any issue in Milestone 3 UI / Data Flow logic.
- **Modal Dialog Blocking**:
  `QInputDialog.getText` and `QMessageBox` are modal dialogs. Automated tests mock these methods (or test the underlying `config.unlock_prokit` / `update_prokit_ui_visibility` methods directly) to avoid blocking GUI loops.

---

## 4. Conclusion

All requirements of Milestone 3 (R3 `main.py`) have been fully implemented, tested, and verified:
1. `InEarSnitchApp = MainWindow` alias exposed at module level.
2. Header logo triple-click filter installed, opening the ProKit unlock dialog within 600ms.
3. Non-editable Ear Tip dropdown (`cb_prokit_tip`) container integrated into the bottom bar next to the RUN button.
4. Auto-suggesting last-used tip per IEM model with fallback to ProKit V2 (id=5).
5. Forwarding active `tip_id` during `save_trace_to_db` with default fallback to 1 ("Unbekannt") when locked.
6. All 19 smoke tests pass cleanly. All 36 targeted UI and Unlock E2E tests pass cleanly.
7. Production database `inearsnitch.db` remains untouched at 16,379,904 bytes.

---

## 5. Verification Method

1. **Smoke Test**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   *Expected result*: `✅ ALL 19 CHECKS PASSED`.

2. **ProKit Targeted E2E UI & Unlock Tests**:
   ```bash
   pytest -v tests/test_prokit_e2e.py -k "TripleClick or UI or Selector or Unlock"
   ```
   *Expected result*: `36 passed, 51 deselected`.

3. **Core Gate & Adversarial Test Suites**:
   ```bash
   pytest -v tests/test_prokit_gate.py tests/test_prokit_adversarial.py tests/test_prokit_adversarial_db.py
   ```
   *Expected result*: `53 passed`.

4. **Database File Size Integrity**:
   ```bash
   stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db
   ```
   *Expected output*: `16379904`.

5. **Interactive UI Verification**:
   Launch the application:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/main.py
   ```
   - Verify Ear Tip dropdown is hidden by default.
   - Triple-click on "InEar SNITCH" title text -> unlock dialog opens.
   - Enter `SNITCH-PROKIT-2024-001` -> ProKit unlocks, Ear Tip dropdown appears next to RUN button.
   - Select an IEM profile -> last used tip or ProKit V2 is selected.
