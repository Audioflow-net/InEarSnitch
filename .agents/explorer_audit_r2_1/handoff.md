# Handoff Report: UI Completeness & Interactive Element Audit (R2)

**Agent ID:** explorer_audit_r2_1  
**Project:** InEar Snitch  
**Working Directory:** `/Users/ben/Desktop/InEarSnitch/.agents/explorer_audit_r2_1`  
**Handoff Type:** Hard (Audit Complete)  

---

## 1. Observation

Direct code and runtime inspection of `/Users/ben/Desktop/InEarSnitch/main.py` (4,622 lines) and `/Users/ben/Desktop/InEarSnitch/analysis_ui.py` (1,804 lines) revealed the following verbatim facts:

1. **Dead Profile Search Field (`main.py:991–1000`)**:
   ```python
   990: search_box = QHBoxLayout()
   991: self.search_input = QLineEdit()
   992: search_input = self.search_input
   993: search_input.setPlaceholderText("Search...")
   994: search_input.setStyleSheet("background-color: #111; color: white; border: 1px solid #333; padding: 5px; border-radius: 4px;")
   995: btn_add_prof = QPushButton("+")
   ...
   1000: search_box.addWidget(search_input)
   ```
   AST inspection shows no `.textChanged`, `.textEdited`, or `.returnPressed` connection anywhere in `main.py`.

2. **Dead Links in Manual Browser (`main.py:1688–1725`)**:
   ```python
   1688: self.manual_browser.setOpenLinks(False)
   1689: def handle_manual_link(url):
   1690:     link = url.toString()
   1691:     file_path = link.split("#")[0]
   1692:     if file_path.startswith("./"):
   1693:         file_path = file_path[2:]
   1694:         
   1695:     if os.path.exists(file_path):
   ...
   1725: self.manual_browser.anchorClicked.connect(handle_manual_link)
   ```
   In `manual_en.md`, `manual_de.md`, and `manual_es.md`, links include `https://squig.link/`, `https://crinacle.com/rankings/iems/`, and anchor `#hardware-guide`. When clicked, `os.path.exists(file_path)` returns `False`. No `QDesktopServices.openUrl(url)` or anchor scroll executes.

3. **Orphaned QLayout & Buttons in `analysis_ui.py:694–756`**:
   ```python
   694: zoom_layout = QHBoxLayout()
   ...
   734: self.btn_reset_zoom = QPushButton("🔍 Autozoom")
   738: self.btn_run_sweep = QPushButton("▶ MEASURE")
   ...
   755: # zoom_layout is intentionally not added to left_pane_layout to avoid double toolbar
   ```
   `zoom_layout` is not added to any widget or layout. `self.btn_reset_zoom` and `self.btn_run_sweep` are never visible.

4. **Shadowed / Duplicate `run_stress_test` in `main.py:2619` vs `main.py:4001`**:
   `main.py` defines `def run_stress_test(self):` at line 2619 (106 lines, uses `StressWorker`, verifies `calibrated_stress_amp`, connects `_on_stress_done`). Line 4001 defines `def run_stress_test(self):` again, which completely replaces the first definition in Python's class dict. Lines 2619–2805 are unreachable dead code.

5. **`AttributeError` in `MusicianCard.on_menu_triggered` (`main.py:278–282`)**:
   ```python
   278: def on_menu_triggered(self, action):
   279:     self.current_iem_id = action.data()
   280:     self.current_iem_name = action.text().replace("", "")
   281:     self.iem_btn.setText(f"{self.current_iem_name} ▾")
   282:     self.iem_changed.emit()
   ```
   `self.iem_btn` is not defined on `MusicianCard`. Calling this method raises `AttributeError`.

6. **Dead / Corrupted Profile Methods in `main.py:3418–3522`**:
   `delete_profile` and `edit_profile` are never called or connected. `edit_profile` contains copy-pasted deletion cleanup at lines 3518–3521 that resets `self.current_iem_id = None` and `self.settings_panel = None`.

7. **Runtime `TypeError` on Profile Tab Switch (`main.py:1478, 2167` -> `profile_ui.py:108`)**:
   ```
   TypeError: 'PySide6.QtWidgets.QLabel.setPixmap' called with wrong argument types:
     PySide6.QtWidgets.QLabel.setPixmap(NoneType)
   ```
   When `create_circular_pixmap` returns `None` (for corrupted/invalid image files), `self.img_label.setPixmap(None)` crashes.

8. **Relative SQLite Path in `analysis_ui.py:1579, 1600, 1681, 1697, 1709`**:
   `conn = sqlite3.connect("inearsnitch.db")` hardcodes relative paths instead of using `self.db.db_path`.

---

## 2. Logic Chain

1. **Dead UI Inputs (Issue 1)**: From Observation 1, `self.search_input` has no signal connections to any filter method. Therefore, users entering text in the musician profile search bar experience an unresponsive interface.
2. **Broken Navigation / Hyperlinks (Issue 2)**: From Observation 2, `setOpenLinks(False)` requires explicit handling in `anchorClicked`. Because `handle_manual_link` gates all logic with `os.path.exists(file_path)`, web URLs and `#anchor` strings fail this check, making all documentation links in the settings manual unresponsive.
3. **Ghost Controls (Issue 3)**: From Observation 3, Qt widgets placed into a QLayout that is neither set on a widget nor nested in a parent layout are orphaned. While `main.py` reparented channel toggle buttons `btn_chan_l`/`btn_chan_r`, it omitted `btn_reset_zoom` and `btn_run_sweep`, leaving dead widget instances in memory.
4. **Method Shadowing / Broken Safety Gates (Issue 4)**: From Observation 4, duplicate method names in a Python class body silently override preceding definitions. The second definition lacks the calibration precondition check and uses `MeasurementWorker` rather than the dedicated `StressWorker`, disabling HOHD peak analysis and leaving `_on_stress_done` uncalled.
5. **Runtime Exceptions (Issues 5 & 7)**: From Observations 5 and 7, accessing non-existent widget members (`self.iem_btn`) or passing `None` to PySide6 methods expecting a `QPixmap` produces fatal unhandled exceptions (`AttributeError` and `TypeError`).

---

## 3. Caveats

- **Scope Boundary**: Audit focused strictly on `main.py` and `analysis_ui.py` per the R2 mission specification. Subordinate UI components in `profile_ui.py`, `history_ui.py`, and `calibration_ui.py` were audited solely at the interface boundaries where `main.py` connects to or triggers them.
- **Audio Hardware**: Hardware-dependent streams (`sounddevice.Stream`) were tested with mock callbacks to avoid audio device locking during CLI execution.
- **No Direct Modifications Made**: Per the strict explorer constraint, zero source code modifications were applied.

---

## 4. Conclusion

The application core UI is largely functional and correctly implements loop lambda variable capture. However, **8 discrete issues** must be resolved before release:
1. **Critical / High Severity**:
   - Fix `main.py` duplicate `run_stress_test` method shadowing to unify calibration checks and Rub & Buzz processing.
   - Fix `profile_ui.py:108` `QLabel.setPixmap` `NoneType` crash when profile images fail to load.
   - Fix `main.py:1688–1725` dead hyperlink handling for external URLs and in-page anchor jumps.
2. **Medium Severity**:
   - Connect `self.search_input` to profile filtering or remove the input widget.
   - Reparent or remove orphaned `AnalysisWidget` zoom and sweep buttons.
   - Remove or fix corrupted/dead `delete_profile` and `edit_profile` methods in `main.py`.
   - Remove obsolete `on_menu_triggered` referencing `self.iem_btn`.
3. **Low Severity**:
   - Unify SQLite database paths in `analysis_ui.py` with `self.db.db_path`.

---

## 5. Verification Method

1. **Smoke Test Execution**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   Confirms baseline integrity (all 19 checks pass).

2. **File & Line Review**:
   - Inspect `main.py` lines 991, 1478, 1688–1725, 2619, 278, 3418, 4001.
   - Inspect `analysis_ui.py` lines 694–756, 1579–1709.
   - Inspect `profile_ui.py` lines 104–110.

3. **Reproduction Commands**:
   - Verify method shadowing:
     ```bash
     python3 -c "import main; mw = main.MainWindow; print('run_stress_test line:', mw.run_stress_test.__code__.co_firstlineno)"
     ```
     *Output:* `run_stress_test line: 4001` (confirming line 2619 is shadowed).
   - Verify missing search input connection:
     ```bash
     python3 -c "with open('main.py') as f: code = f.read(); print('search_input connections:', [l.strip() for l in code.splitlines() if 'search_input' in l and 'connect' in l])"
     ```
     *Output:* `search_input connections: []` (confirming disconnected state).
