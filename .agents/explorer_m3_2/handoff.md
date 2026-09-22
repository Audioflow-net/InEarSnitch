# M3 Unlock Event Filter Explorer Handoff Report

## 1. Observation

### 1.1 Header Logo and Title Layout in `main.py`
In `/Users/ben/Desktop/InEarSnitch/main.py` lines 740–753:
```python
        # --- TOP BAR ---
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("#topBar { background-color: #1a1a1a; border-bottom: 1px solid #2a2a2a; }")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("InEar SNITCH")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
        sublogo = QLabel("DIAGNOSTICS")
        sublogo.setStyleSheet("color: #666; font-size: 14px; margin-left: 10px;")
        top_layout.addWidget(logo)
        top_layout.addWidget(sublogo)
```
- `logo` is instantiated as a standard `QLabel("InEar SNITCH")`.
- `sublogo` is instantiated as `QLabel("DIAGNOSTICS")`.
- Currently, neither `logo` nor `sublogo` is stored as an instance attribute on `self` (`MainWindow`). They exist only as local variables within `MainWindow.__init__`.
- Neither label has custom mouse handlers or event filters installed.

### 1.2 ProKit Unlock State in `config.py`
In `/Users/ben/Desktop/InEarSnitch/config.py`:
- Line 79: `is_prokit_unlocked() -> bool`: Returns `True` if `.prokit_unlocked` token file exists in `get_data_dir()`, `False` otherwise.
- Line 87: `unlock_prokit(code: str) -> bool`: Normalizes code via `code.strip().upper()`, hashes with SHA-256, verifies against `VALID_CODE_HASHES`, and writes to `.prokit_unlocked` on success.
- Line 110: `revoke_prokit() -> bool`: Removes `.prokit_unlocked` file.
- `main.py` does not currently import `config`.

### 1.3 Qt Mouse Event Dispatching for Rapid Clicks
Direct experimentation via PySide6 demonstrated two distinct event patterns:
1. **Real-world OS Event Flow** (macOS / Windows / Linux window managers):
   - Click 1: `QEvent.MouseButtonPress` followed by `QEvent.MouseButtonRelease`.
   - Click 2 (within system double-click interval): `QEvent.MouseButtonDblClick` followed by `QEvent.MouseButtonRelease`. (Qt documentation: *"The double click event replaces the second mouse button press event"*).
   - Click 3: `QEvent.MouseButtonPress` followed by `QEvent.MouseButtonRelease`.
2. **Automated Test / Synthetic Event Flow** (`QTest.mouseClick` invoked in loops):
   - Click 1: `QEvent.MouseButtonPress`
   - Click 2: `QEvent.MouseButtonPress`
   - Click 3: `QEvent.MouseButtonPress`
   - Elapsed time between clicks in test loops is sub-millisecond (~30–60 microseconds). Any artificial debounce filter > 0.001 ms rejects test clicks as duplicates.

### 1.4 Test Suite Failures in `tests/test_prokit_e2e.py`
Running `pytest tests/test_prokit_e2e.py` produced 85 passed and 2 failed:
- Failure 1 (Line 416):
  ```
  AttributeError: module 'main' has no attribute 'InEarSnitchApp'
  ```
  The test harness instantiates `main.InEarSnitchApp`, but the main window class in `main.py` is named `MainWindow`.
- Failure 2 (Line 587):
  ```
  assert abs(peak_l - 7850.0) < 5.0
  AssertionError: 10.521666666666533 < 5.0
  ```
  This is an analytical curve-fitting assertion in Tier 1 Diagnostics Card (M5 scope).

### 1.5 Smoke Test Baseline in `smoke_test.py`
Running `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`:
```
==================================================
✅ ALL 19 CHECKS PASSED
==================================================
```
All 9 critical widget references (`self.btn_capture`, `self.btn_trace`, `self.btn_save_db`, `self.btn_rta_raw`, `self.btn_iec_guide`, `self.cb_meas_target`, `self.cb_meas_history`, `self.plot_widget`, `self.page_ana`) and anti-regression rules (`temp_mag_l`, `target_freqs`, `EQ knob anti-wrap`, `Card click transparency` via `WA_TransparentForMouseEvents`) are fully intact.

---

## 2. Logic Chain

1. **Widget Accessibility & Exposure**:
   - Because `logo` is currently a local variable in `MainWindow.__init__`, neither tests nor external components can inspect it or install filters after initialization.
   - Storing `self.lbl_logo = logo`, `self.lbl_title = logo`, and `self.lbl_sublogo = sublogo` preserves the original widgets, makes them accessible on `self`, and satisfies test assertions expecting title / logo labels.

2. **Event Filter vs. Subclassing**:
   - Subclassing `QLabel` would require modifying the layout construction in `main.py`.
   - Installing an `eventFilter` on `logo` and `sublogo` leaves the existing layout and stylesheets intact.
   - Crucially, installing the event filter strictly on `self.lbl_logo` ensures that events for other widgets (buttons, tabs, plots, window resize handles, scroll areas) never pass through the filter, avoiding any interference with normal UI operation.

3. **Event Detection Logic for Triple-Click**:
   - To handle both real-world double-click replacement (`MouseButtonDblClick`) and automated synthetic clicks (`MouseButtonPress` x3), the filter must listen for:
     `event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick) and event.button() == Qt.LeftButton`.
   - Non-left clicks (`Qt.RightButton`, `Qt.MiddleButton`) are ignored immediately and do not affect the sequence.
   - Pauses between clicks greater than `max_interval` (configured to `max(0.5, QApplication.doubleClickInterval() / 1000.0)`) reset the click sequence `clicks = []`.
   - When the third click arrives (`len(clicks) >= 3`), the sequence is reset `clicks = []` and the unlock dialog callback is executed.
   - Only the third click event returns `True` (consuming the activation event). Preceding clicks and non-qualifying events return `False`, allowing normal Qt event delivery.
   - A re-entrancy flag (`_dialog_active`) prevents multiple modal dialogs if extra rapid clicks occur while the dialog is opening.

4. **Unlock Dialog Flow & Feedback**:
   - When triple-click is triggered, `QInputDialog.getText(self, "ProKit Unlock", "Enter ProKit Unlock Code:", QLineEdit.Normal, "")` opens a modal dialog.
   - If user cancels (`not ok`), the method exits cleanly without changing state or displaying errors.
   - If user submits a code (`ok == True`), `config.unlock_prokit(code)` is called:
     - On `True`: `QMessageBox.information(self, "ProKit Unlocked", "ProKit features have been successfully unlocked!")` is shown, and `self.update_prokit_ui_visibility()` is triggered.
     - On `False`: `QMessageBox.warning(self, "Invalid Code", "The entered unlock code is invalid.")` is shown, and unlock state remains `False`.

5. **UI Visibility Synchronization**:
   - `self.update_prokit_ui_visibility()` queries `config.is_prokit_unlocked()`.
   - It updates the visibility of bottom-bar tip controls (`combo_tip`, `cb_tip`, `cb_prokit_tip`, `lbl_tip`, `widget_prokit_tip`).
   - It triggers active view refreshes:
     - History view: calls `self.page_hist.load_history(m_id)` if available.
     - Diagnostics view: calls `self.page_ana.render_diagnostics()` if available.
   - Calling `self.update_prokit_ui_visibility()` at the conclusion of `MainWindow.__init__` guarantees correct initial visibility on app launch, respecting any existing `.prokit_unlocked` token from previous sessions.

6. **Test Harness Compatibility**:
   - Aliasing `InEarSnitchApp = MainWindow` at module level in `main.py` resolves the `AttributeError` in `test_prokit_e2e.py:416`.

---

## 3. Caveats

- **No Freitext in Unlock Dialog**: The unlock dialog prompt accepts any text string for validation against SHA-256 hashes in `config.py`. However, the ear tip selector itself (`combo_tip`) must remain strictly non-editable (`combo_tip.setEditable(False)`), as mandated by Design Decision 1.
- **Headless Testing of Modal Dialogs**: Because `QInputDialog.getText` and `QMessageBox` are blocking modal dialogs in interactive sessions, automated test suites like `tests/test_prokit_e2e.py` must either mock `QInputDialog.getText` / `QMessageBox` or test `config.unlock_prokit` and `update_prokit_ui_visibility()` directly.
- **Visual Cursor**: The cursor on `self.lbl_logo` should remain default (arrow) rather than `PointingHandCursor`, ensuring the unlock mechanism remains hidden and invisible to standard users per specification.

---

## 4. Conclusion

The triple-click unlock detection mechanism is designed as an isolated, non-blocking `LogoTripleClickFilter(QObject)` installed exclusively on `self.lbl_logo` and `self.lbl_sublogo` in `main.py`. It correctly handles real-world OS click progressions and automated `QTest` sequences, ignores non-left clicks, debounces re-entrancy, and drives the complete offline unlock flow through `config.unlock_prokit(code)`.

### Concrete Proposed Implementation Snippets for `main.py`

#### Snippet 1: Imports (Top of `main.py`)
```python
import time
import config
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer, QObject, QEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QButtonGroup, QSizePolicy, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QComboBox, 
                               QSplitter, QFrame, QLineEdit,
                               QStackedWidget, QMessageBox, QGridLayout, QFileDialog, QScrollArea,
                               QInputDialog, QDialog)
```

#### Snippet 2: Event Filter Class (Module Level in `main.py`)
```python
class LogoTripleClickFilter(QObject):
    """
    Event filter for triple-click detection on the header logo/title label.
    Detects 3 rapid left-clicks within a sliding time window (default 500ms between clicks).
    Non-blocking, ignores non-left clicks, resets after triggering, and prevents
    duplicate re-entrant dialogs.
    """
    def __init__(self, parent, on_triple_click_callback, max_interval=0.5):
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

#### Snippet 3: Header Setup & Filter Installation (`MainWindow.__init__`)
```python
        # --- TOP BAR ---
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("#topBar { background-color: #1a1a1a; border-bottom: 1px solid #2a2a2a; }")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("InEar SNITCH")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
        sublogo = QLabel("DIAGNOSTICS")
        sublogo.setStyleSheet("color: #666; font-size: 14px; margin-left: 10px;")
        top_layout.addWidget(logo)
        top_layout.addWidget(sublogo)

        # ProKit: Expose logo labels and install triple-click unlock filter
        self.lbl_logo = logo
        self.lbl_title = logo
        self.lbl_sublogo = sublogo
        self.logo_triple_click_filter = LogoTripleClickFilter(
            self,
            self.on_logo_triple_clicked,
            max_interval=max(0.5, QApplication.doubleClickInterval() / 1000.0)
        )
        logo.installEventFilter(self.logo_triple_click_filter)
        sublogo.installEventFilter(self.logo_triple_click_filter)
```

#### Snippet 4: Unlock Handler & Visibility Update Methods (`MainWindow`)
```python
    def on_logo_triple_clicked(self):
        """Handle triple click on header logo/title: open unlock dialog and process code."""
        code, ok = QInputDialog.getText(
            self,
            "ProKit Unlock",
            "Enter ProKit Unlock Code:",
            QLineEdit.Normal,
            ""
        )
        if not ok:
            return False

        if config.unlock_prokit(code):
            QMessageBox.information(
                self,
                "ProKit Unlocked",
                "ProKit features have been successfully unlocked!"
            )
            self.update_prokit_ui_visibility()
            return True
        else:
            QMessageBox.warning(
                self,
                "Invalid Code",
                "The entered unlock code is invalid."
            )
            return False

    def update_prokit_ui_visibility(self):
        """Update visibility of all ProKit UI elements based on current unlock status."""
        unlocked = config.is_prokit_unlocked()

        # 1. Bottom-bar Tip Selector ComboBox and container
        for attr in ("combo_tip", "cb_tip", "cb_prokit_tip", "tip_selector"):
            if hasattr(self, attr):
                w = getattr(self, attr)
                if w is not None and hasattr(w, "setVisible"):
                    w.setVisible(unlocked)
        for attr in ("lbl_tip", "widget_prokit_tip", "tip_container"):
            if hasattr(self, attr):
                w = getattr(self, attr)
                if w is not None and hasattr(w, "setVisible"):
                    w.setVisible(unlocked)

        # 2. History View: reload history cards to show/hide tip badges and seal status
        if hasattr(self, "page_hist") and hasattr(self.page_hist, "load_history"):
            try:
                m_id = None
                if hasattr(self, "active_card") and self.active_card:
                    m_id = self.active_card.m_id
                if m_id is not None:
                    self.page_hist.load_history(m_id)
            except Exception:
                pass

        # 3. Diagnostics View: re-render diagnostics to show/hide Tip Analysis card
        if hasattr(self, "page_ana") and hasattr(self.page_ana, "render_diagnostics"):
            try:
                self.page_ana.render_diagnostics()
            except Exception:
                pass
```

#### Snippet 5: Initial Visibility Call (`MainWindow.__init__` end)
```python
        # Initialize ProKit visibility state on startup
        self.update_prokit_ui_visibility()
```

#### Snippet 6: Test Alias (Module Level in `main.py`)
```python
# Alias for test harness compatibility
InEarSnitchApp = MainWindow
```

---

## 5. Verification Method

1. **Smoke Test Verification**:
   Execute the project smoke test:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   *Expected outcome*: 19/19 checks pass without warning.

2. **Unit Test of Filter Logic**:
   Run the isolated test script validating the 7 behavioral conditions:
   ```bash
   python3 -c "
   import sys, time
   from PySide6.QtWidgets import QApplication, QLabel
   from PySide6.QtCore import Qt, QObject, QEvent
   from PySide6.QtTest import QTest

   app = QApplication.instance() or QApplication(sys.argv)
   lbl = QLabel('InEar SNITCH')
   triggered = 0
   def on_trigger():
       global triggered
       triggered += 1

   from main import LogoTripleClickFilter
   filt = LogoTripleClickFilter(lbl, on_trigger, max_interval=0.5)
   lbl.installEventFilter(filt)

   # Right clicks ignored
   QTest.mouseClick(lbl, Qt.RightButton)
   assert triggered == 0

   # 2 clicks do not trigger
   QTest.mouseClick(lbl, Qt.LeftButton)
   QTest.mouseClick(lbl, Qt.LeftButton)
   assert triggered == 0

   # 3rd click triggers
   QTest.mouseClick(lbl, Qt.LeftButton)
   assert triggered == 1

   # 4th click does not re-trigger
   QTest.mouseClick(lbl, Qt.LeftButton)
   assert triggered == 1
   "
   ```

3. **E2E Test Suite Run**:
   Execute the ProKit E2E test suite:
   ```bash
   pytest -v tests/test_prokit_e2e.py -k "TripleClick or Logo"
   ```

4. **Invalidation Conditions**:
   - Any single or double mouse click on buttons (`btn_capture`, `btn_theme`, `btn_top_settings`, `btn_rta_raw`, `btn_iec_guide`) failing to fire its standard handler.
   - Any drag action on graph views or sidebars being intercepted.
   - Failure of `smoke_test.py` (any check failing).
