# Milestone 3 (R3 main.py) — Data Flow & Safety Investigation Report

## 1. Observation

### 1.1 Measurement Saving Flow in `main.py`
In `/Users/ben/Desktop/InEarSnitch/main.py` at line 3847, `save_trace_to_db` currently calls `database.save_measurement`:
```python
3847:     def save_trace_to_db(self):
3848:         if not self.current_iem_id: return
3849:         if self.temp_freqs is None:
3850:             self.sub_lbl.setText("Nothing to save yet — run a measurement first, then hit Save.")
3851:             self.sub_lbl.setStyleSheet("color: red; font-size: 13px;")
3852:             return
3853:             
3854:         gain = "Auto"
3855:         notes = ""
3856:         
3857:         try:
3858:             self.db.save_measurement(
3859:                 self.current_iem_id, 
3860:                 self.temp_freqs, 
3861:                 self.temp_mag_l, 
3862:                 self.temp_mag_r, 
3863:                 self.temp_phase_l, 
3864:                 self.temp_phase_r,
3865:                 gain,
3866:                 notes,
3867:                 ""
3868:             )
```
In `/Users/ben/Desktop/InEarSnitch/database.py` at line 124:
```python
124:     def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path="", tip_id=1):
...
137:         actual_tip_id = tip_id if tip_id is not None else 1
```
Currently, `save_trace_to_db` passes 9 positional parameters (leaving `tip_id` to default to 1), without retrieving or forwarding the active tip selection from the UI.

### 1.2 Profile Switching & IEM Selection in `main.py`
In `/Users/ben/Desktop/InEarSnitch/main.py` at lines 2897–2953, profile changes are handled inside `on_profile_selected(self, card=None)`:
```python
2916:         if card:
2917:             name = card.name
2918:             iem = card.current_iem_name
2919:             iem_id = card.current_iem_id
2920:             
2921:             self.current_iem_name = iem
2922:             self.current_musician_name = name
2923:             self.update_watermark()
2924:             from datetime import datetime
2925:             self.sub_lbl.setText("Status: Ready to measure.")
2926:             self.current_iem_id = iem_id
2927:             
2928:             # Enable buttons since a profile is selected
2929:             self.btn_capture.setEnabled(True)
2930:             if hasattr(self, 'btn_save_tgt'): self.btn_save_tgt.setEnabled(True)
2931:             self.btn_save_db.setEnabled(True)
2932:             
2933:             # Fetch extra data for header
2934:             import sqlite3
2935:             
2936:             # --- AUTO-SELECT TARGET CURVE ---
2937:             if iem:
...
```
`MusicianCard.select_iem` (line 243) and `MusicianCard.on_menu_triggered` (line 251) emit `iem_changed`, which is connected at line 2709:
```python
2709:             card.iem_changed.connect(lambda c=card: self.force_profile_selection(c))
```
`force_profile_selection` (line 2721) invokes `self.on_profile_selected(card)`. Thus, `on_profile_selected` is the single bottleneck where `self.current_iem_id` is updated.

In `database.py` at line 198:
```python
198:     def get_last_used_tip(self, iem_id):
...
208:         cursor.execute("""
209:             SELECT tip_id 
210:             FROM Measurements 
211:             WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
212:             ORDER BY timestamp DESC, id DESC
213:             LIMIT 1
214:         """, (iem_id,))
```
`get_last_used_tip` correctly queries and returns `int(row[0])` or `None` (excluding `id=1`).

### 1.3 Bottom Bar Layout in `main.py`
In `/Users/ben/Desktop/InEarSnitch/main.py` lines 1010–1182:
```python
1166:         left_group = QHBoxLayout()
1167:         left_group.setSpacing(15)
1168:         left_group.setAlignment(Qt.AlignBottom)
1169:         left_group.addLayout(mod_actions)
1170:         left_group.addLayout(mod_compare)
1171:         left_group.addWidget(chan_widget)
1172:         
1173:         right_group = QHBoxLayout()
1174:         right_group.setSpacing(7)
1175:         right_group.addWidget(rta_widget)
1176:         right_group.addLayout(mod_capture)
1177:         
1178:         control_layout.setAlignment(Qt.AlignBottom)
1179:         control_layout.addLayout(left_group)
1180:         control_layout.addStretch()
1181:         control_layout.addLayout(right_group)
```
The RUN button is in `mod_capture`. Placing `self.tip_container` into `right_group` between `rta_widget` and `mod_capture` places the Ear Tip selector immediately adjacent to the RUN button.

### 1.4 Logo and Header Title in `main.py`
In `/Users/ben/Desktop/InEarSnitch/main.py` lines 747–752:
```python
747:         logo = QLabel("InEar SNITCH")
748:         logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
749:         sublogo = QLabel("DIAGNOSTICS")
750:         sublogo.setStyleSheet("color: #666; font-size: 14px; margin-left: 10px;")
751:         top_layout.addWidget(logo)
752:         top_layout.addWidget(sublogo)
```
Currently, `logo` is a local variable. To implement the invisible triple-click unlock easter egg, `logo` should be stored as `self.logo` with an event filter installed.

### 1.5 Test Suite Failures in `tests/test_prokit_e2e.py`
Running `pytest -v tests/test_prokit_e2e.py`:
```
FAILED tests/test_prokit_e2e.py::TestTier1UISelector::test_bottom_bar_tip_widget_creation
AttributeError: module 'main' has no attribute 'InEarSnitchApp'

tests/test_prokit_e2e.py:416:
>       app_win = main.InEarSnitchApp.__new__(main.InEarSnitchApp)
```
In `main.py`, the application class is `class MainWindow(QMainWindow)`. The test assumes `main.InEarSnitchApp` exists. Adding `InEarSnitchApp = MainWindow` at module level directly resolves this error.

---

## 2. Logic Chain

### 2.1 Trace of `tip_id` Retrieval and Safety Fallback
1. Observation 1.1 shows `save_trace_to_db` currently ignores tips and delegates to `save_measurement` with default `tip_id=1`.
2. Requirement R3 and Design Decision 1 specify that when ProKit is locked or when no valid tip is selected, `tip_id` must default to `1` ("Unbekannt").
3. Safety checks must verify:
   - `config.is_prokit_unlocked()` is True
   - `hasattr(self, 'combo_tip')`
   - `self.combo_tip.isVisible()`
   - `self.combo_tip.currentData() is not None`
4. If all 4 conditions hold, `tip_id = int(self.combo_tip.currentData())`. Otherwise, `tip_id = 1`.
5. Passing `tip_id=tip_id` to `self.db.save_measurement(...)` guarantees database consistency.

### 2.2 Profile Switching & Tip Auto-Suggestion
1. Observation 1.2 shows that `self.current_iem_id` is set inside `on_profile_selected(self, card)`.
2. Requirement R3 dictates: auto-suggest the last-used tip for the selected IEM.
3. When `self.current_iem_id` is set:
   - Call `last_tip_id = self.db.get_last_used_tip(self.current_iem_id)`
   - If `last_tip_id` is not None: find index in `self.combo_tip` via `self.combo_tip.findData(last_tip_id)` and set `currentIndex(idx)` if `idx != -1`.
   - If `last_tip_id` is None (or `self.current_iem_id` is None): fallback to default tip `id=5` ("ProKit V2", `is_default == 1`).
   - Find `self.combo_tip.findData(5)`. If present, set `currentIndex(idx)`. If not present, fallback to index `0`.
4. Wrap this in a method `suggest_tip_for_current_iem(self)` and provide an alias `on_iem_changed(self)`.

### 2.3 Bottom-Bar UI Component Specifications
1. Observation 1.3 shows `right_group` holds `rta_widget` and `mod_capture`.
2. Create `self.tip_container = QWidget()` containing:
   - Title label: `QLabel("EAR TIP")`
   - ComboBox: `self.combo_tip = QComboBox()` with `setEditable(False)` (Design Decision 1: freetext is forbidden)
   - Object name: `self.combo_tip.setObjectName("cb_prokit_tip")`
   - Aliases: `self.cb_prokit_tip = self.combo_tip`, `self.cb_tip = self.combo_tip`
3. Populate via `self.populate_tips()`: queries `db.get_all_tips(include_unknown=False)` (excludes id=1).
   - Items added as: `f"{t['icon_char']} {t['name']}", t["id"]`
4. Visibility: `self.tip_container.setVisible(config.is_prokit_unlocked())` and `self.combo_tip.setVisible(config.is_prokit_unlocked())`.

### 2.4 Triple-Click Unlock Dialog
1. Observation 1.4 shows `logo` at line 747. Store as `self.logo` and install event filter.
2. In `MainWindow.__init__`:
   - Initialize `self._logo_clicks = 0`
   - Initialize `self._logo_timer = QTimer(self)` (single-shot, 600ms timeout connecting to `_reset_logo_clicks`)
3. In `eventFilter`:
   - Inspect clicks on `self.logo` and `self.sublogo`.
   - Only increment on `event.button() == Qt.LeftButton`. Right-clicks or other buttons do not increment (Tier 2 test requirement).
   - Click 1: start timer.
   - Click 3: reset counter to 0, stop timer, call `self.open_prokit_unlock_dialog()`.
   - Clicks spaced >600ms: timer fires and resets counter to 0.
   - Rapid 4 clicks: 3rd opens dialog and resets to 0, 4th sets counter to 1 (Tier 2 test requirement).
4. `ProKitUnlockDialog(QDialog)`:
   - Contains `self.line_edit = QLineEdit()`, `self.btn_submit = QPushButton("Unlock")`, `self.btn_cancel = QPushButton("Cancel")`.
   - On submit: `config.unlock_prokit(code)`. If True, `accept()` and trigger `self.update_prokit_visibility()`. If False, display error message in `status_lbl`.

---

## 3. Caveats

1. **Test `test_helmholtz_peak_detection_algorithm`**: In `tests/test_prokit_e2e.py` line 587, the synthetic curve acoustic downward tilt `-(freqs / 1000.0) * 0.4` shifts the peak frequency slightly (10.5 Hz) away from the nominal 7850 Hz peak center, causing an assertion failure in that Tier 1 synthetic test. This belongs to Milestone 5 / DSP diagnostics and does NOT affect Milestone 3 (UI / Data Flow).
2. **Dynamic Propagations**: When `update_prokit_visibility()` is called after an unlock, it should safely guard references to `self.page_hist` and `self.page_ana` using `hasattr`, as these pages are owned by Milestones 4 and 5 respectively.
3. **Smoke Test Compliance**: `smoke_test.py` strictly verifies 9 critical widgets and 4 anti-regression strings. None of these are modified or removed.

---

## 4. Conclusion & Drop-In Code Specifications for Worker

All requirements for Milestone 3 (R3 `main.py`) are fully mapped with precise drop-in code chunks ready for implementation by the Worker.

### Snippet 1: Imports (lines 66–70 in `main.py`)
```python
from PySide6.QtWidgets import (QApplication, QMainWindow, QButtonGroup, QSizePolicy, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QComboBox, 
                               QSplitter, QFrame, QLineEdit, QDialog,
                               QStackedWidget, QMessageBox, QGridLayout, QFileDialog, QScrollArea)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer, QEvent
```

### Snippet 2: `ProKitUnlockDialog` Class (Insert immediately before `class MainWindow(QMainWindow):` at line 634)
```python
class ProKitUnlockDialog(QDialog):
    """
    Offline activation dialog for InEarSnitch ProKit hardware features.
    Accepts 50-character SHA256 hashed serials (SNITCH-PROKIT-2024-001..050).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ProKit Hardware Activation")
        self.setFixedWidth(420)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #3f3f46;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        
        title_lbl = QLabel("ProKit Hardware Activation")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        layout.addWidget(title_lbl)
        
        desc_lbl = QLabel("Enter your hardware license code to unlock ProKit Ear Tip tracking and advanced reproducibility diagnostics:")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #a1a1aa; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_lbl)
        
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("SNITCH-PROKIT-2024-XXX")
        self.line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #27272a;
                color: #ffffff;
                border: 1px solid #3f3f46;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: monospace;
            }
            QLineEdit:focus {
                border-color: #10b981;
            }
        """)
        self.line_edit.returnPressed.connect(self.handle_submit)
        layout.addWidget(self.line_edit)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12px;")
        self.status_lbl.setVisible(False)
        layout.addWidget(self.status_lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #27272a;
                color: #e4e4e7;
                border: 1px solid #3f3f46;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3f3f46;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_submit = QPushButton("Unlock", self)
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #34d399;
            }
        """)
        self.btn_submit.clicked.connect(self.handle_submit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_submit)
        layout.addLayout(btn_layout)

    def handle_submit(self):
        import config
        code = self.line_edit.text()
        if config.unlock_prokit(code):
            self.accept()
        else:
            self.status_lbl.setText("Invalid activation code. Please check and try again.")
            self.status_lbl.setVisible(True)
            self.line_edit.selectAll()
            self.line_edit.setFocus()
```

### Snippet 3: `MainWindow.__init__` Additions (inside `__init__`)
```python
        # Logo triple-click activation detector
        self._logo_clicks = 0
        self._logo_timer = QTimer(self)
        self._logo_timer.setSingleShot(True)
        self._logo_timer.setInterval(600)
        self._logo_timer.timeout.connect(self._reset_logo_clicks)

        # Initialize ProKit visibility & catalog
        self.update_prokit_visibility()
```

### Snippet 4: Top Bar Logo Setup (lines 747–753 in `setup_ui`)
```python
        self.logo = QLabel("InEar SNITCH")
        self.logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
        self.sublogo = QLabel("DIAGNOSTICS")
        self.sublogo.setStyleSheet("color: #666; font-size: 14px; margin-left: 10px;")
        self.logo.installEventFilter(self)
        self.sublogo.installEventFilter(self)
        top_layout.addWidget(self.logo)
        top_layout.addWidget(self.sublogo)
```

### Snippet 5: Bottom Bar Ear Tip Selector (inside `setup_ui` around line 1173)
```python
        # --- MODULE 6: PROKIT EAR TIP SELECTOR ---
        self.tip_container = QWidget()
        self.tip_container.setObjectName("tip_container")
        mod_tip = QVBoxLayout(self.tip_container)
        mod_tip.setContentsMargins(0, 0, 0, 0)
        mod_tip.setSpacing(4)
        
        tip_label = QLabel("EAR TIP")
        tip_label.setStyleSheet("color: #777; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
        tip_label.setAlignment(Qt.AlignCenter)
        
        self.combo_tip = QComboBox()
        self.combo_tip.setObjectName("cb_prokit_tip")
        self.combo_tip.setEditable(False)
        self.combo_tip.setFixedWidth(135)
        self.combo_tip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.combo_tip.setToolTip("Select ProKit Coupler Ear Tip")
        self.combo_tip.setStyleSheet("""
            QComboBox {
                background-color: #222;
                color: #e4e4e7;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                border-color: #10b981;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #222;
                color: #e4e4e7;
                selection-background-color: #10b981;
                selection-color: black;
                border: 1px solid #444;
            }
        """)
        # Compatibility aliases
        self.cb_prokit_tip = self.combo_tip
        self.cb_tip = self.combo_tip
        
        mod_tip.addWidget(tip_label)
        mod_tip.addWidget(self.combo_tip, stretch=1)
        
        right_group = QHBoxLayout()
        right_group.setSpacing(7)
        right_group.addWidget(rta_widget)
        right_group.addWidget(self.tip_container)
        right_group.addLayout(mod_capture)
```

### Snippet 6: ProKit Helper & Event Filter Methods on `MainWindow`
```python
    def _reset_logo_clicks(self):
        self._logo_clicks = 0

    def eventFilter(self, obj, event):
        if hasattr(self, 'logo') and obj in (self.logo, getattr(self, 'sublogo', None)):
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._logo_clicks += 1
                    if self._logo_clicks == 1:
                        self._logo_timer.start()
                    elif self._logo_clicks >= 3:
                        self._logo_clicks = 0
                        self._logo_timer.stop()
                        self.open_prokit_unlock_dialog()
                        return True
        return super().eventFilter(obj, event)

    def open_prokit_unlock_dialog(self):
        dialog = ProKitUnlockDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.update_prokit_visibility()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "ProKit Unlocked", 
                "ProKit Tip-Tracking and Advanced Diagnostics have been successfully unlocked!"
            )

    def update_prokit_visibility(self):
        import config
        unlocked = config.is_prokit_unlocked()
        if hasattr(self, 'tip_container'):
            self.tip_container.setVisible(unlocked)
        if hasattr(self, 'combo_tip'):
            self.combo_tip.setVisible(unlocked)
            if unlocked:
                self.populate_tips()
                self.suggest_tip_for_current_iem()
        if hasattr(self, 'page_hist') and hasattr(self.page_hist, 'load_history'):
            if hasattr(self, 'active_card') and self.active_card and hasattr(self.active_card, 'm_id'):
                self.page_hist.load_history(self.active_card.m_id)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'render_diagnostics'):
            self.page_ana.render_diagnostics()

    def populate_tips(self):
        if not hasattr(self, 'combo_tip') or not hasattr(self, 'db'):
            return
        cur_id = self.combo_tip.currentData()
        self.combo_tip.blockSignals(True)
        self.combo_tip.clear()
        tips = self.db.get_all_tips(include_unknown=False) if hasattr(self.db, 'get_all_tips') else []
        for t in tips:
            display_text = f"{t.get('icon_char', '')} {t.get('name', '')}".strip()
            self.combo_tip.addItem(display_text, t["id"])
            
        if cur_id is not None and self.combo_tip.findData(cur_id) != -1:
            self.combo_tip.setCurrentIndex(self.combo_tip.findData(cur_id))
        else:
            def_idx = self.combo_tip.findData(5)  # ProKit V2 default
            if def_idx != -1:
                self.combo_tip.setCurrentIndex(def_idx)
            elif self.combo_tip.count() > 0:
                self.combo_tip.setCurrentIndex(0)
        self.combo_tip.blockSignals(False)

    def suggest_tip_for_current_iem(self):
        if not hasattr(self, 'combo_tip') or not hasattr(self, 'db'):
            return
        if not getattr(self, 'current_iem_id', None):
            def_idx = self.combo_tip.findData(5)
            if def_idx != -1:
                self.combo_tip.setCurrentIndex(def_idx)
            return
            
        last_tip = self.db.get_last_used_tip(self.current_iem_id) if hasattr(self.db, 'get_last_used_tip') else None
        if last_tip is not None:
            idx = self.combo_tip.findData(last_tip)
            if idx != -1:
                self.combo_tip.setCurrentIndex(idx)
                return
                
        def_idx = self.combo_tip.findData(5)
        if def_idx != -1:
            self.combo_tip.setCurrentIndex(def_idx)
        elif self.combo_tip.count() > 0:
            self.combo_tip.setCurrentIndex(0)

    def on_iem_changed(self):
        self.suggest_tip_for_current_iem()
```

### Snippet 7: `on_profile_selected` Integration (inside `on_profile_selected` around line 2927)
```python
            self.current_iem_name = iem
            self.current_musician_name = name
            self.update_watermark()
            from datetime import datetime
            self.sub_lbl.setText("Status: Ready to measure.")
            self.current_iem_id = iem_id
            
            # Auto-suggest tip for current IEM
            self.suggest_tip_for_current_iem()
```

### Snippet 8: `save_trace_to_db` Integration (lines 3857–3869 in `main.py`)
```python
        try:
            import config
            tip_id = 1
            if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and self.combo_tip.isVisible():
                val = self.combo_tip.currentData()
                if val is not None:
                    tip_id = int(val)

            self.db.save_measurement(
                self.current_iem_id, 
                self.temp_freqs, 
                self.temp_mag_l, 
                self.temp_mag_r, 
                self.temp_phase_l, 
                self.temp_phase_r,
                gain,
                notes,
                "",
                tip_id=tip_id
            )
            self.sub_lbl.setText("Status: Saved to Database.")
            self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")
```

### Snippet 9: Top-Level Module Class Alias (at the end of `main.py` before `if __name__ == "__main__":`)
```python
# External and test suite compatibility alias
InEarSnitchApp = MainWindow
```

---

## 5. Verification Method

### 5.1 Smoke Test Execution
Execute the mandatory smoke test to ensure no regression on existing widgets and data flows:
```bash
python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
```
**Expected**: 19/19 checks pass (`ALL 19 CHECKS PASSED`).

### 5.2 Milestone 3 Unit & Integration Tests
Execute the comprehensive E2E test suite focusing on UI selector, triple-click unlock, auto-suggestion, and measurement save flow:
```bash
pytest -v tests/test_prokit_e2e.py -k "UI or Logo or Selector or TripleClick"
```
**Expected**: All targeted tests pass.

### 5.3 Full Test Suite Execution
```bash
pytest -v tests/test_prokit_gate.py tests/test_prokit_adversarial.py tests/test_prokit_adversarial_db.py
```
**Expected**: 100% pass across all M1 and M2 test modules (53/53 passed).

### 5.4 Invalidation Conditions
- If `smoke_test.py` fails on widget references (e.g. `self.btn_capture` or `self.btn_save_db`).
- If `tip_id` falls back to anything other than `1` when ProKit is locked or unselected.
- If freetext input can be entered into `self.combo_tip`.
- If `InEarSnitchApp` cannot be instantiated in tests.
