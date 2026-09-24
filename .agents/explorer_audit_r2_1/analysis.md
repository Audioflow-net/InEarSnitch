# Detailed UI Completeness & Interactive Element Audit Report (R2)

**Auditor:** explorer_audit_r2_1  
**Target Files:** `/Users/ben/Desktop/InEarSnitch/main.py` (4,622 lines), `/Users/ben/Desktop/InEarSnitch/analysis_ui.py` (1,804 lines)  
**Date:** 2026-09-24  
**Integrity Mode:** Benchmark / Read-Only Audit  

---

## 1. Executive Summary

A comprehensive, line-by-line and AST-verified audit of all interactive UI elements (`QPushButton`, `QComboBox`, `QCheckBox`, `QLineEdit`, `QButtonGroup`, `QAction`, and custom controls) in `main.py` and `analysis_ui.py` was conducted.

A total of **62 interactive elements and signal pathways** were audited (42 in `main.py`, 20 in `analysis_ui.py`).
The audit revealed **8 notable issues**, ranging from dead UI controls and disconnected hyperlinks to duplicate shadowed method definitions, unhandled `TypeError` crashes, and legacy `AttributeError` traps.

No pure `NotImplementedError` or `pass` placeholder functions were found, and lambda loop closures correctly captured loop variables via default arguments (`n=name`, `c=card`, `b=band`). However, severe behavioral and structural defects were identified in signal routing, layout containment, and click event handling.

---

## 2. Complete Inventory of Identified Issues

### Issue 1: Disconnected / Dead Search Input Widget in Musician Profiles Sidebar
* **Widget Name:** `self.search_input` (`QLineEdit`)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/main.py`
* **Line Number(s):** Lines 991–994, 1000
* **Code Snippet:**
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
* **Expected Behavior:** Typing into the search field should filter `self.profile_cards` in real-time or on Enter to quickly locate musicians and IEM models.
* **Actual Behavior:** The `QLineEdit` is instantiated, styled, and inserted into the UI layout, but is NEVER connected to any signal (`textChanged`, `textEdited`, or `returnPressed`). User input produces zero effect (dead UI widget).
* **Severity:** Medium

---

### Issue 2: Dead Links in Settings Manual Browser (`QTextBrowser` link handler)
* **Widget Name:** `self.manual_browser` (`QTextBrowser`)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/main.py`
* **Line Number(s):** Lines 1688–1725
* **Code Snippet:**
  ```python
  1688: self.manual_browser.setOpenLinks(False)
  1689: def handle_manual_link(url):
  1690:     link = url.toString()
  1691:     file_path = link.split("#")[0]
  1692:     if file_path.startswith("./"):
  1693:         file_path = file_path[2:]
  1694:         
  1695:     if os.path.exists(file_path):
  1696:         with open(file_path, "r", encoding="utf-8") as f:
  1697:             self.manual_browser.setMarkdown(f.read())
  1698:         
  1699:         # If there's a chapter 14 anchor, scroll to it
  1700:         if "#14" in link:
  ...
  1710:         elif "#hardware-guide" in link:
  ...
  1725: self.manual_browser.anchorClicked.connect(handle_manual_link)
  ```
* **Expected Behavior:** 
  1. Clicking external documentation links present in `manual_en.md`, `manual_de.md`, and `manual_es.md` (e.g., `https://squig.link/`, `https://crinacle.com/rankings/iems/`, `https://www.head-fi.org/`, `https://www.audiosciencereview.com/`) should launch the user's default web browser via `QDesktopServices.openUrl(url)`.
  2. Clicking in-page relative anchor links like `[Hardware Guide](#hardware-guide)` in the localized manual files should scroll the viewport to the target header.
* **Actual Behavior:**
  1. `setOpenLinks(False)` disables default Qt browser handling.
  2. `handle_manual_link` only executes logic `if os.path.exists(file_path):`. For external URLs (`https://...`), `os.path.exists` returns `False`, and there is no `QDesktopServices` fallback; clicks are completely ignored (dead links).
  3. For in-page anchor links starting with `#`, `file_path` is `""`. `os.path.exists("")` evaluates to `False`, preventing internal anchor navigation from executing; clicks are completely ignored (dead links).
* **Severity:** High

---

### Issue 3: Orphaned / Detached Toolbar Buttons in `AnalysisWidget`
* **Widget Name(s):** `self.btn_reset_zoom` (`QPushButton("🔍 Autozoom")`), `self.btn_run_sweep` (`QPushButton("▶ MEASURE")`), `self.cb_ana_target` (`QComboBox`), `self.cb_ana_history` (`QComboBox`)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/analysis_ui.py`
* **Line Number(s):** Lines 694–756
* **Code Snippet:**
  ```python
  694:  zoom_layout = QHBoxLayout()
  695:  zoom_layout.setSpacing(6)
  ...
  734:  self.btn_reset_zoom = QPushButton("🔍 Autozoom")
  735:  self.btn_reset_zoom.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; }")
  736:  self.btn_reset_zoom.clicked.connect(self.reset_zoom)
  ...
  738:  self.btn_run_sweep = QPushButton("▶ MEASURE")
  739:  self.btn_run_sweep.hide()
  ...
  749:  zoom_layout.addWidget(self.seg_widget)
  750:  zoom_layout.addWidget(self.cb_ana_target)
  751:  zoom_layout.addWidget(self.cb_ana_history)
  752:  zoom_layout.addWidget(self.btn_run_sweep)
  753:  zoom_layout.addStretch()
  754:  zoom_layout.addWidget(self.btn_reset_zoom)
  755:  # zoom_layout is intentionally not added to left_pane_layout to avoid double toolbar
  756:  # We will extract its buttons into the tab corner widget in main.py
  ```
* **Expected Behavior:** Buttons defined for the analysis view (especially `self.btn_reset_zoom`) should be accessible within the visible user interface or cleanly refactored.
* **Actual Behavior:** `zoom_layout` is created as an unparented `QHBoxLayout` and never attached to `left_pane_layout` or any widget. In `main.py` (lines 1446–1462), only `self.page_ana.btn_chan_l` and `btn_chan_r` are reparented into the corner widget. `self.page_ana.btn_reset_zoom` and `self.page_ana.btn_run_sweep` remain stranded in the detached `zoom_layout` and are completely invisible on screen.
* **Severity:** Medium

---

### Issue 4: Duplicate Shadowed Method: `run_stress_test` Overwrites Dedicated Worker Pipeline
* **Widget Name(s):** `self.btn_stress` (`QPushButton("STRESS")`, line 1329) and `self.page_ana.btn_stress_test` (`QPushButton("STRESS TEST")`, line 823)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/main.py`
* **Line Number(s):** Lines 2619–2725 (First Definition) vs 4001–4011 (Second Definition)
* **Code Snippet:**
  ```python
  # Line 2619: First definition (Comprehensive StressWorker + calibration check + HOHD)
  2619: def run_stress_test(self):
  2620:     """Run a high-amplitude sweep and extract HOHD for Rub & Buzz detection."""
  2621:     stress_amp = getattr(self.audio_engine, 'calibrated_stress_amp', None)
  2622:     if stress_amp is None:
  2623:         QMessageBox.warning(self, "Not Calibrated Yet", ...)
  ...
  2719:     self._stress_worker = StressWorker(...)
  2722:     self._stress_worker.finished.connect(self._on_stress_done)
  2723:     self._stress_worker.error.connect(self._on_stress_error)
  ...

  # Line 4001: Second definition (Overwrites the first definition at class creation time)
  4001: def run_stress_test(self):
  4002:     from PySide6.QtWidgets import QMessageBox
  4003:     reply = QMessageBox.critical(self, "ACHTUNG: STRESS TEST", ...)
  4010:     if reply == QMessageBox.Yes:
  4011:         self.run_measurement(is_stress_test=True)
  ```
* **Expected Behavior:** A unified stress test method that provides hearing safety warnings, verifies calibration preconditions, and executes stress sweep analysis.
* **Actual Behavior:** Python class method shadowing causes line 4001 to silently replace lines 2619–2725. As a result, the 106-line first implementation containing `StressWorker`, `_on_stress_done` (line 2727), and `_on_stress_error` (line 2791) becomes unreachable dead code. Furthermore, clicking `btn_stress` calls line 4001 which bypasses the calibration safety check (`calibrated_stress_amp`).
* **Severity:** High

---

### Issue 5: AttributeError Crash in `MusicianCard.on_menu_triggered`
* **Widget Name:** `MusicianCard` (Line 278)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/main.py`
* **Line Number(s):** Lines 278–282
* **Code Snippet:**
  ```python
  278: def on_menu_triggered(self, action):
  279:     self.current_iem_id = action.data()
  280:     self.current_iem_name = action.text().replace("", "")
  281:     self.iem_btn.setText(f"{self.current_iem_name} ▾")
  282:     self.iem_changed.emit()
  ```
* **Expected Behavior:** Card selection updates current IEM state without referencing deleted attributes.
* **Actual Behavior:** `self.iem_btn` does not exist on `MusicianCard` (the UI was converted to `AvatarButton` instances in `self.avatar_btns`). Any invocation of this slot immediately crashes with:
  `AttributeError: 'MusicianCard' object has no attribute 'iem_btn'`.
* **Severity:** Medium

---

### Issue 6: Dead Code & State Corruption in Profile Operations (`edit_profile` / `delete_profile`)
* **Widget Name / Methods:** `main.py:delete_profile` (lines 3418–3437) and `main.py:edit_profile` (lines 3439–3522)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/main.py`
* **Line Number(s):** Lines 3418–3522
* **Code Snippet:**
  ```python
  3514:     conn.close()
  3515:     self.load_profiles_from_db()
  3516:     self.plot_widget.clear()
  3517:     
  3518:     self.sub_lbl.setText("Profile deleted successfully.")
  3519:     self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 13px;")
  3520:     self.current_iem_id = None
  3521:     self.settings_panel = None
  ```
* **Expected Behavior:** Profile editing and deletion are managed inside `profile_ui.py`. Unused methods in `main.py` should be purged or maintained correctly.
* **Actual Behavior:** Neither `delete_profile` nor `edit_profile` is connected to any button or shortcut in `main.py`. Moreover, `edit_profile` ends with copy-pasted deletion cleanup (lines 3518–3521) that displays "Profile deleted successfully.", resets `self.current_iem_id = None`, and sets `self.settings_panel = None`, which would corrupt the main window state if ever executed.
* **Severity:** Medium

---

### Issue 7: Unhandled TypeError Crash When Clicking "PROFILE" Tab (`self.btn_nav_prof`)
* **Widget Name:** `self.btn_nav_prof` (`QPushButton("PROFILE")`, line 1031)
* **File Path:** `/Users/ben/Desktop/InEarSnitch/main.py` (lines 1478, 2167) and `/Users/ben/Desktop/InEarSnitch/profile_ui.py` (lines 106–108)
* **Line Number(s):** `main.py:1478, 2167`; `profile_ui.py:106–108`
* **Code Snippet:**
  ```python
  # main.py:1478
  1478: self.btn_nav_prof.clicked.connect(lambda: self.switch_workspace_tab(0))

  # main.py:2167
  2167: self.page_prof.load_profile(self.current_iem_id, m_id)

  # profile_ui.py:106-108
  106: circ_pix = create_circular_pixmap(reader, self.size_val)
  107: 
  108: self.img_label.setPixmap(circ_pix)
  ```
* **Expected Behavior:** Switching tabs gracefully loads musician profiles. If an image file path in the database is corrupted, unreadable, or invalid, `create_circular_pixmap` returns `None`, and the avatar should safely fallback to `QPixmap()`.
* **Actual Behavior:** PySide6 does not accept `None` in `QLabel.setPixmap()`. Clicking `btn_nav_prof` triggers:
  `TypeError: 'PySide6.QtWidgets.QLabel.setPixmap' called with wrong argument types: PySide6.QtWidgets.QLabel.setPixmap(NoneType)`
  This crashes the tab transition handler.
* **Severity:** High

---

### Issue 8: Database Path Inconsistency in AnalysisWidget EQ Preset Handlers
* **Widget Name(s):** `self.btn_save_eq` (`save_eq_preset`), `btn_load` (`apply_eq_preset`), `btn_del` (`delete_eq_preset`), `init_eq_db`, `load_eq_presets`
* **File Path:** `/Users/ben/Desktop/InEarSnitch/analysis_ui.py`
* **Line Number(s):** Lines 1579, 1600, 1681, 1697, 1709
* **Code Snippet:**
  ```python
  1579: conn = sqlite3.connect("inearsnitch.db")
  1600: conn = sqlite3.connect("inearsnitch.db")
  1681: conn = sqlite3.connect("inearsnitch.db")
  1697: conn = sqlite3.connect("inearsnitch.db")
  1709: conn = sqlite3.connect("inearsnitch.db")
  ```
* **Expected Behavior:** Database connections should reference the central configured database path (`self.db.db_path` or `config.get_data_dir()`), as implemented in `TipAnalysisCardWidget` (line 534: `conn = sqlite3.connect(self.db.db_path)`).
* **Actual Behavior:** Hardcoding `"inearsnitch.db"` causes SQLite to create or read a database relative to whatever current working directory the process was launched from, causing preset loss or `sqlite3.OperationalError` if launched outside the project root.
* **Severity:** Low

---

## 3. Systematic Verification of the 4 Audit Categories

| Audit Category | Result | Key Details |
|---|---|---|
| **1. Dead Links / Missing Signal Connections / Unhandled Clicks** | **3 Issues Found** | • `self.search_input` in `main.py:991` has no signal connection.<br>• `self.manual_browser` in `main.py:1725` ignores all external URLs and in-page anchor links.<br>• `self.btn_reset_zoom` & `self.btn_run_sweep` in `analysis_ui.py:734,738` are trapped in an orphaned layout. |
| **2. NotImplementedError / 'pass' / Placeholder Logic** | **Clean** | • No pure `NotImplementedError` or `pass` stubs found in active functions.<br>• `delete_profile` and `edit_profile` in `main.py` are dead code with misplaced logic. |
| **3. Broken Lambda Closures in UI Loops** | **Clean** | • EQ band knobs (`analysis_ui.py:955`): default arg `idx=i` captured correctly.<br>• Preset card buttons (`analysis_ui.py:1649,1653`): `n=name` captured correctly.<br>• Musician card clicks (`main.py:2939,2942`): `c=card` captured correctly.<br>• Diagnostic card clicks (`analysis_ui.py:1284`): `b=band, c=cat` captured correctly. |
| **4. Signature Mismatches & Missing Arguments** | **2 Issues Found** | • `QLabel.setPixmap(NoneType)` crash in `profile_ui.py:108` triggered by `main.py:1478` (`btn_nav_prof`).<br>• `AttributeError: iem_btn` in `MusicianCard.on_menu_triggered` (`main.py:281`). |

---

## 4. Full Inventory of Interactive Widgets

### `main.py`
| Widget Name | Type | Line | Signal / Trigger | Target Handler | Audit Status |
|---|---|---|---|---|---|
| `self.btn_theme` | QPushButton | 895 | `.clicked` | `self.on_theme_toggle` | Verified OK |
| `self.btn_top_settings` | QPushButton | 903 | `.clicked` | `_toggle_settings` | Verified OK |
| `self.lbl_logo` | QLabel | 877 | EventFilter (3x) | `self.prompt_prokit_unlock` | Verified OK |
| `self.search_input` | QLineEdit | 991 | None | None | **DEAD WIDGET** |
| `btn_add_prof` | QPushButton | 995 | `.clicked` | `self.open_add_profile_dialog` | Verified OK |
| `self.btn_nav_prof` | QPushButton | 1031 | `.clicked` | `switch_workspace_tab(0)` | **CRASHES ON NONE PIXMAP** |
| `self.btn_nav_ana` | QPushButton | 1033 | `.clicked` | `switch_workspace_tab(2)` | Verified OK |
| `self.btn_nav_hist` | QPushButton | 1035 | `.clicked` | `switch_workspace_tab(3)` | Verified OK |
| `self.cb_smooth` | QComboBox | 1103 | `.currentIndexChanged` | `self.on_smooth_changed` | Verified OK |
| `self.btn_reset_view` | QPushButton | 1109 | `.clicked` | `self.reset_graph_view` | Verified OK |
| `self.btn_trace` | QPushButton | 1178 | `.clicked` | `self.clear_trace` | Verified OK |
| `self.btn_save_db` | QPushButton | 1184 | `.clicked` | `self.save_trace_to_db` | Verified OK |
| `self.cb_meas_target` | QComboBox | 1197 | `.currentIndexChanged` | `self.on_meas_target_changed` | Verified OK |
| `self.cb_meas_history` | QComboBox | 1204 | `.currentIndexChanged` | `self.on_meas_history_changed` | Verified OK |
| `self.btn_l` | QPushButton | 1224 | In `btn_grp_chan` | `update_watermark` / `on_target_channel_changed` | Verified OK |
| `self.btn_r` | QPushButton | 1228 | In `btn_grp_chan` | `update_watermark` / `on_target_channel_changed` | Verified OK |
| `self.combo_tip` | QComboBox | 1243 | `.currentIndexChanged` | `_on_bottom_bar_tip_changed` | Verified OK |
| `self.btn_rta_raw` | QPushButton | 1296 | `.clicked` | `self.on_rta_button_clicked` | Verified OK |
| `self.btn_iec_guide` | QPushButton | 1304 | `.clicked` | `self.on_rta_button_clicked` | Verified OK |
| `self.btn_capture` | QPushButton | 1323 | `.clicked` | `self.run_measurement` | Verified OK |
| `self.btn_stress` | QPushButton | 1329 | `.clicked` | `self.run_stress_test` | **METHOD SHADOWING** |
| `btn_1x, 3x, 5x` | QPushButton | 1351 | In `btn_grp_sweeps` | `get_current_sweeps` | Verified OK |
| `self.settings_dimmer` | QPushButton | 1486 | `.clicked` | `lambda: hide panels` | Verified OK |
| `self.btn_tour` | QPushButton | 1508 | `.clicked` | `self.start_guided_tour` | Verified OK |
| `self.in_combo` | QComboBox | 1543 | `.currentIndexChanged` | `lambda: selected_in_idx` | Verified OK |
| `self.out_combo` | QComboBox | 1551 | `.currentIndexChanged` | `lambda: selected_out_idx` | Verified OK |
| `btn_refresh_dev` | QPushButton | 1559 | `.clicked` | `self.populate_devices` | Verified OK |
| `self.chk_normalize` | QCheckBox | 1571 | None (State read) | `save_settings` / `on_measurement_finished` | Verified OK |
| `self.mic_cal_combo` | QComboBox | 1593 | `.currentIndexChanged` | `self.update_cal_preview` | Verified OK |
| `self.btn_auto_cal` | QPushButton | 1631 | `.clicked` | `self._run_level_calibration` | Verified OK |
| `self.manual_search` | QLineEdit | 1646 | `.textChanged` / `returnPressed` | `on_manual_search` | Verified OK |
| `btn_reload_manual` | QPushButton | 1662 | `.clicked` | `_reload_manual` | Verified OK |
| `self.manual_browser` | QTextBrowser | 1679 | `.anchorClicked` | `handle_manual_link` | **DEAD LINKS (WEB & ANCHORS)** |
| `btn_backup` | QPushButton | 1758 | `.clicked` | `self.backup_database` | Verified OK |
| `btn_restore` | QPushButton | 1763 | `.clicked` | `self.restore_database` | Verified OK |
| `self.search_targets` | QLineEdit | 1775 | `.textChanged` | `self.filter_target_list` | Verified OK |
| `btn_import_tgt` | QPushButton | 1787 | `.clicked` | `self.import_target_template` | Verified OK |
| `btn_export_tgt` | QPushButton | 1791 | `.clicked` | `self.export_target_template` | Verified OK |
| `btn_delete_tgt` | QPushButton | 1795 | `.clicked` | `self.delete_target_template` | Verified OK |
| `btn_save_set` | QPushButton | 1833 | `.clicked` | `self.save_settings` | Verified OK |

### `analysis_ui.py`
| Widget Name | Type | Line | Signal / Trigger | Target Handler | Audit Status |
|---|---|---|---|---|---|
| `self.dial` | RelativeDial | 72 | `.valueChanged` | `_on_dial_changed` | Verified OK |
| `self.txt_val` | QLineEdit | 82 | `.editingFinished` | `_on_txt_changed` | Verified OK |
| `self.cb_tip_selector` | QComboBox | 254 | `.currentIndexChanged` | `_on_tip_combo_changed` | Hidden (by design) |
| `self.graph_tabs` | QTabWidget | 682 | `.currentChanged` | `render_diagnostics` | Verified OK |
| `self.btn_chan_l` | QPushButton | 707 | `.toggled` | `refresh_view` / `render_diagnostics` | Reparented in main.py corner |
| `self.btn_chan_r` | QPushButton | 713 | `.toggled` | `refresh_view` / `render_diagnostics` | Reparented in main.py corner |
| `self.cb_ana_target` | QComboBox | 722 | `.currentIndexChanged` (main) | `on_ana_target_changed` | Hidden (by design) |
| `self.cb_ana_history` | QComboBox | 728 | `.currentIndexChanged` (main) | `on_ana_history_changed` | Hidden (by design) |
| `self.btn_reset_zoom` | QPushButton | 734 | `.clicked` | `self.reset_zoom` | **DETACHED / ORPHANED LAYOUT** |
| `self.btn_run_sweep` | QPushButton | 738 | `.clicked` | `self.request_measurement.emit` | **DETACHED / ORPHANED LAYOUT** |
| `self.btn_stress_test` | QPushButton | 819 | `.clicked` | `self.request_stress_test.emit` | Verified OK |
| `self.btn_toggle_tools` | QPushButton | 856 | `.clicked` | `self.toggle_tools_pane` | Verified OK |
| `self.btn_dsp_master` | QPushButton | 907 | `.toggled` | `on_master_toggle` | Verified OK |
| `cb_on` (B1-B5) | QPushButton | 928 | `.toggled` | `update_dsp` | Verified OK |
| `knob_f` (B1-B5) | FloatKnob | 941 | `.valueChanged` | `update_dsp` | Verified OK |
| `knob_g` (B1-B5) | FloatKnob | 942 | `.valueChanged` | `update_dsp` | Verified OK |
| `knob_q` (B1-B5) | FloatKnob | 943 | `.valueChanged` | `update_dsp` | Verified OK |
| `self.le_preset_name` | QLineEdit | 1009 | None (Read on save) | `self.save_eq_preset` | Verified OK |
| `self.btn_save_eq` | QPushButton | 1012 | `.clicked` | `self.save_eq_preset` | Relative DB Path discrepancy |
| `btn_load` | QPushButton | 1647 | `.clicked` | `self.apply_eq_preset(n)` | Relative DB Path discrepancy |
| `btn_del` | QPushButton | 1651 | `.clicked` | `self.delete_eq_preset(n)` | Relative DB Path discrepancy |
