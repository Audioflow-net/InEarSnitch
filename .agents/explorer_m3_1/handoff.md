# Milestone 3 (R3 main.py) UI Layout & Specification Mining Report

## Executive Summary
This report provides the authoritative specification, UI layout analysis, widget placement design, data flow mechanics, anti-regression guards, and test verification requirements for Milestone 3 (R3 `main.py`) in the InEarSnitch ProKit Tip-Tracking project.

---

## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | UI Layout | Bottom Bar Tip Container (`tip_container`) | QWidget container placed in `right_group` adjacent to RUN button block (`mod_capture`) | None | Container holding label & ComboBox | Hidden cleanly when ProKit locked | `main.py:1166-1182` |
| 2 | UI Component | Non-editable Tip Selector (`combo_tip` / `cb_tip`) | QComboBox with `setEditable(False)` populated from `TipProfiles` | User selection click | Selected item change, emits signal | Freitext strictly disabled | `ORIGINAL_REQUEST.md:20`, `test_prokit_e2e.py:422-427` |
| 3 | UI Integration | Object Name Compliance (`cb_prokit_tip`) | Object name set to `"cb_prokit_tip"` for UI automation and tests | None | `objectName() == "cb_prokit_tip"` | None | `test_prokit_e2e.py:419` |
| 4 | Data Flow | Catalog Population (`populate_tip_selector`) | Populates ComboBox using `DatabaseManager.get_all_tips()` with formatted string (`f"{icon_char} {name}"`) and stores `tip['id']` as `userData` | Catalog list from SQLite | ComboBox items populated with IDs | Empty DB yields 0 items safely | `ORIGINAL_REQUEST.md:96`, `database.py:174-196` |
| 5 | Security / Gate | ProKit Visibility Toggling (`update_prokit_visibility`) | Toggles visibility of `tip_container` / `combo_tip` according to `config.is_prokit_unlocked()` | `config.is_prokit_unlocked()` | UI widget `.setVisible(bool)` | Falls back to hidden if token missing | `ORIGINAL_REQUEST.md:96`, `test_prokit_e2e.py:440-455` |
| 6 | UX / Auto-Suggest | Last-Used Tip Auto-Suggestion | In `on_profile_selected()`, queries `db.get_last_used_tip(iem_id)` and auto-selects that tip | `iem_id` | ComboBox index updated to match | If None (new IEM or legacy only), falls back to default tip (id=5) | `ORIGINAL_REQUEST.md:97`, `database.py:198-216` |
| 7 | Data Flow | Measurement Persistence (`save_trace_to_db`) | Extracts `combo_tip.currentData()` and forwards `tip_id` to `db.save_measurement(..., tip_id=tip_id)` | Active measurement buffers + selected tip | Row inserted into `Measurements` with `tip_id` | If locked/empty, defaults safely to `tip_id=1` | `main.py:3847-3868`, `database.py:124-150` |
| 8 | Activation UI | Triple-Click Logo Filter (`TripleClickFilter`) | Event filter on `logo` label detecting 3 left-clicks within 500ms | QMouseEvent (`MouseButtonPress`) | Opens `ProKitUnlockDialog` | Right-clicks and slow clicks ignored | `ORIGINAL_REQUEST.md:99`, `test_prokit_e2e.py:470-512` |
| 9 | Activation UI | ProKit Unlock Dialog (`ProKitUnlockDialog`) | Modal QDialog containing `QLineEdit`, `QPushButton("Unlock")`, and `QPushButton("Cancel")` | User input code | Unlocks ProKit via `config.unlock_prokit(code)` | Shows warning on invalid code | `ORIGINAL_REQUEST.md:99`, `test_prokit_e2e.py:488-512` |
| 10 | Compatibility | App Class Alias (`InEarSnitchApp = MainWindow`) | Module-level alias in `main.py` allowing E2E test harness instantiation | None | Module export `main.InEarSnitchApp` | Eliminates AttributeError in E2E tests | `test_prokit_e2e.py:416` |

---

## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Tip Selector | Empty `TipProfiles` table in database | `combo_tip.count() == 0`, `combo_tip.currentData() is None`, UI does not crash (`test_selector_empty_database_fallback`). |
| 2 | Auto-Suggest | IEM with 0 measurements in database | `db.get_last_used_tip(iem_id)` returns `None`. UI gracefully selects default tip (`is_default == 1`, id=5 `ProKit V2`). |
| 3 | Auto-Suggest | IEM with only legacy measurements (`tip_id == 1`) | `get_last_used_tip(iem_id)` excludes id=1 and returns `None`. UI selects default tip (id=5) instead of suggesting "Unbekannt". |
| 4 | Tip Selector | Rapid user selection switching | `setCurrentIndex()` handles 50 rapid changes without UI freeze or signal loop (`test_selector_rapid_data_switching`). |
| 5 | Visibility Gate | Token file modified while app running | When unlock dialog completes or visibility refreshes, `tip_container` updates instantly without window reload (`test_unlock_lifecycle_toggles_ui_selector`). |
| 6 | Triple-Click | Clicks spaced > 500ms apart | Timer expires, `click_count` resets to 0, unlock dialog does NOT open (`test_slow_clicks_do_not_trigger_triple_click`). |
| 7 | Triple-Click | Right-clicks or middle-clicks on logo | Filter specifically checks `event.button() == Qt.LeftButton`, ignores non-left clicks (`test_non_left_click_ignored`). |
| 8 | Triple-Click | 4 rapid left-clicks on logo | Exactly 1 dialog opens; click counter resets to 0 on 3rd click; 4th click becomes count=1 of next cycle (`test_quad_click_only_opens_one_dialog`). |
| 9 | Unlock Dialog | License code entered with whitespace or lowercase | Normalized by `config.unlock_prokit()` (stripped & uppercased), succeeds cleanly (`test_dialog_whitespace_code_submission`). |
| 10 | Trace Save | Measurement saved while ProKit locked | `save_trace_to_db` detects locked status or `combo_tip.currentData() is None`, passes `tip_id=1` ("Unbekannt") to `save_measurement`. |

---

## 1. Observation
1. **Bottom Bar Layout Architecture (`main.py:1010–1187`)**:
   - The toolbar container is `self.control_panel = QFrame()` (objectName `"ControlPanel"`).
   - Layout is `control_layout = QHBoxLayout(self.control_panel)` with margins `(15, 12, 15, 12)` and spacing `20`.
   - Layout composition:
     - `left_group = QHBoxLayout()` with spacing `15`, `Qt.AlignBottom`:
       - `mod_actions = QVBoxLayout()`: `self.btn_trace` (width 85px) and `self.btn_save_db` (width 85px).
       - `mod_compare = QVBoxLayout()`: `self.cb_meas_target` and `self.cb_meas_history` (min 100px, max 340px).
       - `chan_widget = QWidget()`: `self.btn_l` and `self.btn_r` segmented buttons.
     - `control_layout.addStretch()`
     - `right_group = QHBoxLayout()` with spacing `7`:
       - `rta_widget = QWidget()`: `self.btn_rta_raw` and `self.btn_iec_guide` (width 95px).
       - `mod_capture = QVBoxLayout()` with spacing `4`:
         - `self.btn_capture = QPushButton("RUN")` (width 220px, height expanding, font-size 24px).
         - `sweeps_widget = QWidget()` (width 220px, buttons 1x, 3x, 5x).
   - The RUN button (`self.btn_capture`) is anchored in `mod_capture` on the far right.

2. **Smoke Test Critical References (`smoke_test.py:53–61`)**:
   - `smoke_test.py` scans `main.py` source text using `f"{w} ="` for exactly 9 widget assignments:
     1. `self.btn_capture = QPushButton("RUN")` (`main.py:1132`)
     2. `self.btn_trace = QPushButton("✗ CLEAR")` (`main.py:1039`)
     3. `self.btn_save_db = QPushButton("⤓ SAVE")` (`main.py:1045`)
     4. `self.btn_rta_raw = QPushButton("RTA")` (`main.py:1109`)
     5. `self.btn_iec_guide = QPushButton("Depth")` (`main.py:1117`)
     6. `self.cb_meas_target = QComboBox()` (`main.py:1058`)
     7. `self.cb_meas_history = QComboBox()` (`main.py:1065`)
     8. `self.plot_widget = pg.PlotWidget(...)` (`main.py:996`)
     9. `self.page_ana = AnalysisWidget()` (`main.py:1193`)
   - Current status: `python3 smoke_test.py` passes 19/19 checks.
   - *Note on prompt nominal list*: The prompt mentioned names (`combo_musician`, `combo_iem`, `btn_capture`, `input_gain`, `btn_toggle_phase`, `btn_undo`, `btn_redo`, `btn_auto_scale`, `theme_selector`). None of those names (except `btn_capture`) exist in `InEarSnitch`. The app uses `MusicianCard` sidebar items, automatic view bounds, and `self.btn_theme`. The actual 9 widgets tested by `smoke_test.py` are the 9 listed above. All 9 must be preserved untouched.

3. **Logo Label Location (`main.py:747–753`)**:
   - In `setup_ui()`, the top header bar contains:
     `logo = QLabel("InEar SNITCH")`
     `sublogo = QLabel("DIAGNOSTICS")`
   - Currently `logo` is a local variable.

4. **Profile Selection Flow (`main.py:2897–2987`)**:
   - `on_profile_selected(self, card=None)` sets `self.current_iem_id = iem_id` at line 2926 and enables buttons (`self.btn_capture.setEnabled(True)`).
   - This is the exact injection point for auto-suggesting the last-used tip for `iem_id`.

5. **Measurement Persistence Flow (`main.py:3847–3868`)**:
   - `save_trace_to_db(self)` calls `self.db.save_measurement(...)` at line 3858 without `tip_id`.
   - `database.py:124` defines: `def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path="", tip_id=1):`.
   - Extending the call to pass `tip_id=tip_id` completes the data pipeline.

6. **Current Test Status (`pytest tests/test_prokit_e2e.py`)**:
   - 85 of 87 tests PASS.
   - Failure 1: `test_bottom_bar_tip_widget_creation` fails with `AttributeError: module 'main' has no attribute 'InEarSnitchApp'`.
   - Failure 2: `test_helmholtz_peak_detection_algorithm` (diagnostics card test belonging to M5).

---

## 2. Logic Chain
1. **Placement of `combo_tip`**:
   - *Constraint*: Must be near `btn_capture` (`ORIGINAL_REQUEST.md:96`), only visible when unlocked (`ORIGINAL_REQUEST.md:96`), and cannot distort bottom bar height.
   - *Observation*: `right_group` contains `rta_widget` (width 95px) and `mod_capture` (width 220px).
   - *Deduction*: Placing `self.tip_container` into `right_group` directly to the left of `mod_capture` (i.e., `right_group.addWidget(rta_widget)`, `right_group.addWidget(self.tip_container)`, `right_group.addLayout(mod_capture)`) positions the tip selector directly adjacent to the RUN button block.
   - *Structure*: `self.tip_container = QWidget()` with vertical layout containing:
     1. Small uppercase label `lbl_tip = QLabel("EAR TIP")` matching `create_group_label()`.
     2. `self.combo_tip = QComboBox()`, `self.cb_tip = self.combo_tip`, `setObjectName("cb_prokit_tip")`.
   - When unlocked, it takes ~140px width. When locked, `self.tip_container.setVisible(False)` collapses it with zero leftover margins or empty gaps.

2. **Non-editable Requirement**:
   - `ORIGINAL_REQUEST.md` Design Decision 1 (LOCKED): "Freitext is FORBIDDEN — Tips are always from the TipProfiles catalog table."
   - `combo_tip.setEditable(False)` must be set upon creation. `isEditable()` returns `False`.

3. **Populating `combo_tip`**:
   - `self.db.get_all_tips(include_unknown=True)` returns 5 dicts:
     - `{'id': 1, 'name': 'Unbekannt', 'icon_char': '?', 'is_default': False, ...}`
     - `{'id': 2, 'name': 'Kein Aufsatz', 'icon_char': '○', 'is_default': False, ...}`
     - `{'id': 3, 'name': 'Standard Foam', 'icon_char': '▲', 'is_default': False, ...}`
     - `{'id': 4, 'name': 'ProKit V1', 'icon_char': '◆', 'is_default': False, ...}`
     - `{'id': 5, 'name': 'ProKit V2', 'icon_char': '★', 'is_default': True, ...}`
   - Format: `display_text = f"{icon_char} {name}".strip()` (e.g. `"★ ProKit V2"`).
   - User data: `self.combo_tip.addItem(display_text, userData=tip['id'])`.
   - Default selection logic: Scan for item with `is_default == 1` (or `id == 5`). If found, call `setCurrentIndex(idx)`.
   - *Catalog filtering note*: Whether `include_unknown=True` (5 items) or `include_unknown=False` (4 items) is used, ProKit V2 (id=5, `is_default == 1`) will always be identified and selected as default.

4. **Dynamic Visibility Toggling**:
   - Gate function: `config.is_prokit_unlocked()`.
   - `update_prokit_visibility(self)` executes:
     `self.tip_container.setVisible(config.is_prokit_unlocked())`
   - Called during initial UI setup and immediately upon closing a successful unlock dialog.

5. **Auto-Suggest Logic**:
   - In `on_profile_selected(self, card)`:
     - Check `last_tip_id = self.db.get_last_used_tip(self.current_iem_id)`.
     - `database.py` guarantees `get_last_used_tip()` filters out `tip_id = 1` ("Unbekannt").
     - If `last_tip_id` is found, search `self.combo_tip.itemData(i) == last_tip_id` and select it.
     - If `last_tip_id is None` (new IEM or only legacy measurements), fallback to default tip (`is_default == 1`, id=5 `ProKit V2`).

6. **Saving Measurement with Active Tip**:
   - In `save_trace_to_db(self)`:
     ```python
     tip_id = 1
     if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and self.combo_tip is not None:
         tip_val = self.combo_tip.currentData()
         if tip_val is not None:
             tip_id = tip_val
     ```
     Pass `tip_id=tip_id` into `self.db.save_measurement(...)`.

7. **Triple-Click Logo Unlock**:
   - In `setup_ui()`, assign `self.lbl_logo = logo`.
   - Install an event filter `TripleClickFilter(self, timeout_ms=500)` on `self.lbl_logo`.
   - Event filter detects left button presses within 500ms. On 3rd click, stops timer, resets count, and calls `self.open_prokit_unlock_dialog()`.
   - Dialog provides `QLineEdit`, `btn_submit = QPushButton("Unlock")`, `btn_cancel = QPushButton("Cancel")`.
   - On submit, calls `config.unlock_prokit(code)`. If True, accepts dialog and invokes `self.update_prokit_visibility()`.

8. **Fixing E2E Test Failure `main.InEarSnitchApp`**:
   - In `main.py`, define `InEarSnitchApp = MainWindow` at module level.
   - This immediately resolves `AttributeError: module 'main' has no attribute 'InEarSnitchApp'` in `test_bottom_bar_tip_widget_creation`.

---

## 3. Caveats
1. **Smoke Test Assignment String Matching**:
   `smoke_test.py` strictly checks for literal `self.btn_capture =`, `self.btn_trace =`, etc. Do not reformat these lines or change them to unpacked tuple assignments.
2. **Offline Unlock State Persistence**:
   `config.is_prokit_unlocked()` checks for the `.prokit_unlocked` token file in `config.get_data_dir()`. Tests mock `get_data_dir()` to a temporary directory. The UI code must call `config.is_prokit_unlocked()` dynamically rather than caching the boolean at import time.
3. **`include_unknown` in Catalog**:
   `database.py:get_all_tips` defaults to `include_unknown=True`. For measurement tip selection, if the user wishes to hide "Unbekannt" from the dropdown (since a user measuring with the coupler never uses an "unknown" tip), `include_unknown=False` can be used. Both options are supported by the default selection logic.
4. **No Code Implementation**:
   Per Specification Miner protocol, no production files were modified during this task.

---

## 4. Conclusion
1. **Bottom-Bar Placement**:
   Place `self.tip_container` into `right_group` directly to the left of `mod_capture` (`btn_capture` / RUN block).
   Container holds `lbl_tip = QLabel("EAR TIP")` and `self.combo_tip = QComboBox()`.
   Aliases: `self.cb_tip = self.combo_tip`, `setObjectName("cb_prokit_tip")`.
   Set `self.combo_tip.setEditable(False)`.
2. **Population & Default**:
   Populate via `db.get_all_tips()`. Display `f"{icon_char} {name}".strip()`, store integer `t['id']` in `userData`.
   Default to tip with `is_default == 1` (id=5, "★ ProKit V2").
3. **Visibility**:
   Controlled by `self.tip_container.setVisible(config.is_prokit_unlocked())`.
4. **Auto-Suggest**:
   In `on_profile_selected()`, query `db.get_last_used_tip(iem_id)`. If found, select it; if None, fallback to id=5.
5. **Persistence**:
   In `save_trace_to_db()`, extract `tip_id = self.combo_tip.currentData()` and forward `tip_id=tip_id` to `save_measurement()`.
6. **Triple-Click Unlock**:
   Install event filter on `self.lbl_logo`, open modal dialog with `QLineEdit`, "Unlock", and "Cancel" buttons. On success, call `update_prokit_visibility()`.
7. **Smoke Test Preservation**:
   All 9 critical widget references checked by `smoke_test.py` (`self.btn_capture`, `self.btn_trace`, `self.btn_save_db`, `self.btn_rta_raw`, `self.btn_iec_guide`, `self.cb_meas_target`, `self.cb_meas_history`, `self.plot_widget`, `self.page_ana`) remain 100% untouched.
8. **E2E Compatibility**:
   Add `InEarSnitchApp = MainWindow` at module level in `main.py` to satisfy `test_bottom_bar_tip_widget_creation`.

---

## 5. Verification Method
1. **Smoke Test**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   Must yield `✅ ALL 19 CHECKS PASSED`.
2. **Targeted E2E Tests (UI & Logo)**:
   ```bash
   pytest -v tests/test_prokit_e2e.py -k "UI or Logo"
   ```
3. **Full E2E Suite**:
   ```bash
   pytest -v tests/test_prokit_e2e.py
   ```
4. **Headless Visual / Widget Tree Check**:
   ```python
   from PySide6.QtWidgets import QApplication
   import main
   app = QApplication.instance() or QApplication([])
   win = main.MainWindow()
   assert win.combo_tip is not None
   assert win.combo_tip.isEditable() is False
   assert win.combo_tip.objectName() == "cb_prokit_tip"
   ```
