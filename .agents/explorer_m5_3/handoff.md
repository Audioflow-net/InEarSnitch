# Milestone 5 (R5 analysis_ui.py) UI Card & Reactivity Design Report

## 1. Observation

### 1.1 `analysis_ui.py` Diagnostics Hierarchy & Layout Structure
- **Container Structure** (`analysis_ui.py:360-375`):
  ```python
  self.diag_container = QWidget()
  diag_layout = QVBoxLayout(self.diag_container)
  diag_layout.setContentsMargins(4, 4, 4, 4)
  self.report_scroll = QScrollArea()
  self.report_scroll.setWidgetResizable(True)
  self.report_container = QWidget()
  self.report_layout = QVBoxLayout(self.report_container)
  self.report_scroll.setWidget(self.report_container)
  diag_layout.addWidget(self.report_scroll)
  self.tools_tabs.addTab(self.diag_container, "Diagnostics")
  ```
- **Lifecycle in `render_diagnostics()`** (`analysis_ui.py:622-729`):
  - Line 637–640: Clears previous diagnostic cards on each render:
    ```python
    while self.report_layout.count():
        item = self.report_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
    ```
  - Line 642–643: Early return if `_last_report` is empty:
    ```python
    if not hasattr(self, '_last_report') or not self._last_report:
        return
    ```
    *Critical note*: When ProKit is unlocked, even before a live measurement is executed, historical tip data (Helmholtz median, reproducibility score, seal history) exists in the database for the active IEM profile. The guard must allow ProKit tip analysis card rendering if `config.is_prokit_unlocked()` is True.
  - Line 650–652: Tab categorization:
    ```python
    tab_idx = self.graph_tabs.currentIndex()
    tab_cat_map = {0: 'FR', 1: 'THD', 2: 'CSD'}
    active_cat = tab_cat_map.get(tab_idx, None)
    ```
    Coupler tip tracking and Helmholtz resonance belong to Frequency Response (`FR`) / general acoustics.

### 1.2 Back-End Analytical API Contracts in `database.py`
The Milestone 2 queries are implemented and verified in `database.py`:
1. `get_tip_target_peak(iem_id, tip_id)` (`database.py:415-471`):
   - Computes median Helmholtz resonance peak in 6,000 Hz – 10,000 Hz window.
   - Returns: `{"left": float | None, "right": float | None}` (e.g. `{"left": 8050.0, "right": 8120.0}`).
2. `get_reproducibility_scores(iem_id, tip_id)` (`database.py:242-326`):
   - Band-limited strictly to 20 Hz – 8,000 Hz on common grid.
   - Left and Right channels strictly separate.
   - Returns `None` if $N < 5$ measurements.
   - Returns `{"left": {"score": float, "std_dev": float, "count": int, "is_preliminary": bool}, "right": ...}` if $N \ge 5$.
   - `is_preliminary = True` if $5 \le N \le 9$; `is_preliminary = False` if $N \ge 10$.
3. `get_seal_history(iem_id, tip_id)` (`database.py:328-413`):
   - Evaluates 40 Hz vs 500 Hz delta ($\Delta = \text{val}_{40} - \text{val}_{500}$).
   - Returns `{"left": list[dict], "right": list[dict]}` with `delta_db`, `val_40`, `val_500`, `seal_ok`, `status` ("OK" vs "LEAK").
4. `get_all_tips(include_unknown=True)` (`database.py:199-223`):
   - Returns list of catalog dicts: `{"id", "name", "material", "color_hex", "icon_char", "is_default"}`.

### 1.3 Reactivity & Invocation Points in `main.py`
- Line 1300: `self.page_ana.main_window = self`.
- Line 4103–4107: In `update_prokit_ui_visibility()`:
  ```python
  if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'render_diagnostics'):
      try:
          self.page_ana.render_diagnostics()
      except Exception:
          pass
  ```
- Lines 4086–4090: Bottom-bar tip selector is toggled via `config.is_prokit_unlocked()`.
- Lines 4147–4184: `suggest_tip_for_current_iem()` auto-suggests last-used tip for current IEM.

### 1.4 Baseline Test Execution
- `smoke_test.py`: 19/19 checks passed.
- `pytest tests/test_prokit_e2e.py -k "Diagnostics"`: 11/11 tests passed.
- PySide6 operates cleanly in headless mode with `QT_QPA_PLATFORM=offscreen`.

---

## 2. Logic Chain

### 2.1 Visual Card Structure & Information Hierarchy
The Tip Analysis card must provide an intuitive, high-density acoustic diagnostic interface positioned at the top of the Diagnostics report:

1. **Card Frame & Header**:
   - Dark theme container matching InEarSnitch aesthetic (`#18181b` card background, `#27272a` border, `8px` rounded corners).
   - `[PROKIT]` pill badge (`#0ea5e9` background, white bold text).
   - Card title: `"ProKit Ear Tip Analysis"` (`font-size: 12px; font-weight: bold;`).
   - Integrated Tip Selector: `QComboBox` (`#cb_tip_selector`) listing all catalog tips with icons (e.g. `"▮ V26 Straight (Silicone)"`).
     - Allows instant inspection of metrics across different tips without leaving the Diagnostics tab.
     - Automatically syncs with `main_window.combo_tip` when available.

2. **Section 1: Helmholtz Resonance Peak (6 kHz – 10 kHz)**:
   - Evaluates half-wave coupler insertion resonance.
   - Reference target: **8,000 Hz** (IEC-711 coupler standard).
   - Left and Right channels displayed separately in dedicated sub-panels:
     - Left (`#3b82f6`): Detected peak in Hz (e.g. `8,120 Hz`), deviation indicator `Δ +120 Hz`.
     - Right (`#ef4444`): Detected peak in Hz (e.g. `8,050 Hz`), deviation indicator `Δ +50 Hz`.
   - Deviation Status Pill Badges:
     - $|\Delta| \le 200\text{ Hz}$: Green badge `background: #065f46; color: #34d399;` (`"Optimal"`).
     - $200 < |\Delta| \le 500\text{ Hz}$: Yellow badge `background: #451a03; color: #fbbf24;` (`"Acceptable"`).
     - $|\Delta| > 500\text{ Hz}$: Red badge `background: #7f1d1d; color: #f87171;` (`"Shifted: Check Depth"`).

3. **Section 2: Coupling Reproducibility (20 Hz – 8 kHz)** (Locked Decisions 2, 5, 6):
   - Band-limited strictly to 20 Hz – 8,000 Hz.
   - Left and Right channels strictly separated.
   - State Handling:
     - **Empty State ($N < 5$ measurements)**:
       Renders warning box:
       `"Not enough data (min. 5 measurements required, currently N={count})"`
       (Matches `TestTier2DiagnosticsBoundaries.test_diagnostics_missing_data_warning_message` verbatim).
     - **Preliminary State ($5 \le N \le 9$ measurements)**:
       Displays Left Score: `L: 94.2% (±0.4 dB)` and Right Score: `R: 92.8% (±0.5 dB)`.
       Warning pill badge: `[⚠ Preliminary (N={count})]` in amber/yellow (`#f59e0b` / `#451a03`).
       Tooltip: `"Score is preliminary (5–9 measurements). 10+ recommended for stable statistics."`
     - **Stable / Verified State ($N \ge 10$ measurements)**:
       Displays Left Score and Right Score.
       Status pill badge: `[✓ Stable (N={count})]` in emerald green (`#10b981` / `#065f46`).

4. **Section 3: Acoustic Seal History (40 Hz vs 500 Hz)**:
   - Summary display:
     - Left: `L: 5/5 OK (100%) — Mean Δ: +2.8 dB`
     - Right: `R: 4/5 OK (80%) — Mean Δ: -0.5 dB`
   - Trend Micro-Chips:
     - Mini pills for the most recent measurements showing status (`OK` vs `LEAK`) and delta (e.g. `[✓ +3.0] [✓ +2.8] [✗ -14.2]`).
     - Tooltips with timestamp, delta, and status.

### 2.2 Dynamic Reactivity Flow
1. **Unlock State Gating**:
   - `config.is_prokit_unlocked()` controls visibility.
   - If False: No card is created or displayed; Diagnostics shows standard report cards only.
   - If True: `TipAnalysisCardWidget` is instantiated and embedded at the top of `self.report_layout`.
   - On triple-click unlock / revocation: `main.py` invokes `self.page_ana.render_diagnostics()`, updating the view instantly without app restart.
2. **Tip Selection Reactivity**:
   - Changing the tip in `cb_tip_selector` immediately calls `refresh_metrics()`, updating the peak, reproducibility score, and seal history for the selected tip and active IEM.
   - When `main.py` changes the active tip, `AnalysisWidget` syncs with it.
3. **IEM Switch Reactivity**:
   - When the user selects a different IEM profile, `set_active_iem(iem_id)` refreshes the card.
4. **Measurement Sweep Reactivity**:
   - When a measurement completes, `update_analysis()` calls `refresh_view()`, which calls `render_diagnostics()`.
   - Live sweep data (`freqs`, `mag_l`, `mag_r`) updates the live peak detection while database metrics update with the new take.
5. **Robustness & Edge-Case Resilience**:
   - Flat spectra, mono sweeps, corrupt BLOBs, or zero measurements are handled with safe fallbacks and empty-state placeholders. No unhandled exceptions can crash the UI.

---

## 3. Caveats

1. **Standalone Widget Testing without `main_window`**:
   - In automated unit tests, `AnalysisWidget` or `TipAnalysisCardWidget` may be instantiated without an active `main.MainWindow()`.
   - The widget must accept optional `db`, `iem_id`, and `tip_id` parameters, with fallback to `DatabaseManager()` so standalone tests run smoothly.
2. **Empty Diagnostics Report on Cold Start**:
   - In `analysis_ui.py:642`, `render_diagnostics()` currently returns immediately if `not self._last_report`.
   - The guard must be updated to `if (not hasattr(self, '_last_report') or not self._last_report) and not is_prokit: return`. This allows the ProKit card to show historical tip statistics even before running the first live sweep.
3. **Tab Filtering**:
   - The Tip Analysis card should render when `active_cat in ('FR', None)`. When the user switches to Distortion (THD) or Waterfall (CSD), the card is hidden or omitted to prevent layout clutter.

---

## 4. Conclusion & PySide6 Implementation

The visual card design, styling, and dynamic reactivity are fully formulated. Below is the production-ready code ready for the Worker to integrate into `analysis_ui.py`.

### 4.1 Concrete PySide6 `TipAnalysisCardWidget` Code

```python
import numpy as np
import theme
import config
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal


class TipAnalysisCardWidget(QFrame):
    """
    ProKit Ear Tip Analysis & Acoustic Coupling Card.
    Displays:
    1. Helmholtz Resonance Peak (6-10 kHz) relative to 8,000 Hz IEC-711 reference.
    2. Band-Limited Reproducibility Score (20 Hz - 8,000 Hz) with L/R separation,
       empty state (<5 takes), and preliminary warning badge (5-9 takes).
    3. Acoustic Seal History Trend (40 Hz vs 500 Hz delta) with L/R separation.
    """
    tip_changed = Signal(int)

    TARGET_HELMHOLTZ_HZ = 8000.0

    @staticmethod
    def detect_helmholtz_peak(freqs, mag):
        """Detect local peak frequency in 6,000 Hz - 10,000 Hz window."""
        if freqs is None or mag is None:
            return None
        try:
            if len(freqs) < 10 or len(mag) != len(freqs):
                return None
            mask = (freqs >= 6000.0) & (freqs <= 10000.0)
            if not np.any(mask):
                return None
            sub_f = freqs[mask]
            sub_m = mag[mask]
            idx = int(np.argmax(sub_m))
            return float(sub_f[idx])
        except Exception:
            return None

    def __init__(self, parent=None, db=None, iem_id=1, tip_id=1, freqs=None, mag_l=None, mag_r=None):
        super().__init__(parent)
        self.setObjectName("tip_analysis_card")
        self.db = db
        self.iem_id = iem_id or 1
        self.tip_id = tip_id or 1
        self.freqs = freqs
        self.mag_l = mag_l
        self.mag_r = mag_r

        self.setVisible(config.is_prokit_unlocked())
        self._init_ui()
        self.populate_tips()
        self.refresh_metrics()

    def _init_ui(self):
        is_light = theme.is_light() if hasattr(theme, 'is_light') else False
        bg_card = "#ffffff" if is_light else "#18181b"
        border_card = "#e4e4e7" if is_light else "#27272a"
        bg_sub = "#f4f4f5" if is_light else "#1f1f23"
        fg_pri = "#18181c" if is_light else "#ffffff"
        fg_sec = "#52525b" if is_light else "#888888"

        self.setStyleSheet(f"""
            QFrame#tip_analysis_card {{
                background-color: {bg_card};
                border: 1px solid {border_card};
                border-radius: 8px;
                margin: 2px 0px 6px 0px;
            }}
            QFrame.sub_section {{
                background-color: {bg_sub};
                border: 1px solid {border_card};
                border-radius: 6px;
                padding: 6px 8px;
            }}
            QComboBox#cb_tip_selector {{
                background-color: {'#e4e4e7' if is_light else '#27272a'};
                color: {fg_pri};
                border: 1px solid {border_card};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
                min-width: 140px;
            }}
            QComboBox#cb_tip_selector::drop-down {{ border: none; }}
            QComboBox#cb_tip_selector QAbstractItemView {{
                background-color: {bg_sub};
                color: {fg_pri};
                selection-background-color: #0ea5e9;
                border: 1px solid {border_card};
            }}
        """)

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(6)

        # ── Header Row ──────────────────────────────────────────────
        hdr_layout = QHBoxLayout()
        hdr_layout.setSpacing(6)

        tag_lbl = QLabel("PROKIT")
        tag_lbl.setStyleSheet("background: #0ea5e9; color: white; font-size: 9px; font-weight: 900; border-radius: 3px; padding: 2px 5px; letter-spacing: 1px;")
        hdr_layout.addWidget(tag_lbl)

        title_lbl = QLabel("Ear Tip Analysis & Acoustic Coupling")
        title_lbl.setStyleSheet(f"color: {fg_pri}; font-weight: bold; font-size: 11px;")
        hdr_layout.addWidget(title_lbl)

        hdr_layout.addStretch()

        self.cb_tip_selector = QComboBox()
        self.cb_tip_selector.setObjectName("cb_tip_selector")
        self.cb_tip_selector.setToolTip("Select Ear Tip Profile for Analysis")
        self.cb_tip_selector.currentIndexChanged.connect(self._on_tip_combo_changed)
        hdr_layout.addWidget(self.cb_tip_selector)
        card_layout.addLayout(hdr_layout)

        # ── Section 1: Helmholtz Resonance Peak (6-10 kHz) ──────────
        sec1 = QFrame()
        sec1.setObjectName("sec_helmholtz")
        sec1.setProperty("class", "sub_section")
        s1_layout = QVBoxLayout(sec1)
        s1_layout.setContentsMargins(6, 4, 6, 4)
        s1_layout.setSpacing(4)

        s1_title = QLabel("HELMHOLTZ RESONANCE PEAK (IEC-711)")
        s1_title.setStyleSheet("color: #06b6d4; font-size: 10px; font-weight: 900; letter-spacing: 1px;")
        s1_layout.addWidget(s1_title)

        grid1 = QHBoxLayout()
        grid1.setSpacing(8)

        # Left Peak Box
        self.lbl_peak_l = QLabel("L: — Hz")
        self.lbl_peak_l.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: bold;")
        self.badge_peak_delta_l = QLabel("—")
        self.badge_peak_delta_l.setStyleSheet("background: #27272a; color: #71717a; border-radius: 3px; padding: 1px 4px; font-size: 9px;")
        box_l = QHBoxLayout()
        box_l.addWidget(self.lbl_peak_l)
        box_l.addWidget(self.badge_peak_delta_l)
        box_l.addStretch()
        grid1.addLayout(box_l)

        # Right Peak Box
        self.lbl_peak_r = QLabel("R: — Hz")
        self.lbl_peak_r.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: bold;")
        self.badge_peak_delta_r = QLabel("—")
        self.badge_peak_delta_r.setStyleSheet("background: #27272a; color: #71717a; border-radius: 3px; padding: 1px 4px; font-size: 9px;")
        box_r = QHBoxLayout()
        box_r.addWidget(self.lbl_peak_r)
        box_r.addWidget(self.badge_peak_delta_r)
        box_r.addStretch()
        grid1.addLayout(box_r)

        s1_layout.addLayout(grid1)

        self.lbl_peak_target = QLabel("Target: 8,000 Hz (Half-Wave Coupler Resonance)")
        self.lbl_peak_target.setStyleSheet(f"color: {fg_sec}; font-size: 9px;")
        s1_layout.addWidget(self.lbl_peak_target)
        card_layout.addWidget(sec1)

        # ── Section 2: Reproducibility Score (20 Hz - 8 kHz) ────────
        sec2 = QFrame()
        sec2.setObjectName("sec_reproducibility")
        sec2.setProperty("class", "sub_section")
        s2_layout = QVBoxLayout(sec2)
        s2_layout.setContentsMargins(6, 4, 6, 4)
        s2_layout.setSpacing(4)

        s2_hdr = QHBoxLayout()
        s2_title = QLabel("COUPLING REPRODUCIBILITY (20 Hz – 8 kHz)")
        s2_title.setStyleSheet("color: #10b981; font-size: 10px; font-weight: 900; letter-spacing: 1px;")
        s2_hdr.addWidget(s2_title)
        s2_hdr.addStretch()

        self.badge_repro_status = QLabel("")
        self.badge_repro_status.setObjectName("badge_repro_preliminary")
        self.badge_repro_status.hide()
        s2_hdr.addWidget(self.badge_repro_status)
        s2_layout.addLayout(s2_hdr)

        self.lbl_repro_empty = QLabel("")
        self.lbl_repro_empty.setObjectName("lbl_repro_warning")
        self.lbl_repro_empty.setStyleSheet("background: #27200a; border: 1px dashed #d97706; border-radius: 4px; padding: 4px 8px; color: #fbbf24; font-size: 10px;")
        self.lbl_repro_empty.hide()
        s2_layout.addWidget(self.lbl_repro_empty)

        self.repro_scores_widget = QWidget()
        scores_layout = QHBoxLayout(self.repro_scores_widget)
        scores_layout.setContentsMargins(0, 0, 0, 0)
        scores_layout.setSpacing(12)

        self.lbl_score_l = QLabel("L: —")
        self.lbl_score_l.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: bold;")
        self.lbl_score_r = QLabel("R: —")
        self.lbl_score_r.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: bold;")

        scores_layout.addWidget(self.lbl_score_l)
        scores_layout.addWidget(self.lbl_score_r)
        scores_layout.addStretch()
        s2_layout.addWidget(self.repro_scores_widget)
        card_layout.addWidget(sec2)

        # ── Section 3: Acoustic Seal History (40 Hz vs 500 Hz) ──────
        sec3 = QFrame()
        sec3.setObjectName("sec_seal_history")
        sec3.setProperty("class", "sub_section")
        s3_layout = QVBoxLayout(sec3)
        s3_layout.setContentsMargins(6, 4, 6, 4)
        s3_layout.setSpacing(4)

        s3_title = QLabel("ACOUSTIC SEAL HISTORY (40 Hz vs 500 Hz)")
        s3_title.setStyleSheet("color: #a855f7; font-size: 10px; font-weight: 900; letter-spacing: 1px;")
        s3_layout.addWidget(s3_title)

        seal_grid = QHBoxLayout()
        seal_grid.setSpacing(12)

        self.lbl_seal_summary_l = QLabel("L: —")
        self.lbl_seal_summary_l.setStyleSheet("color: #3b82f6; font-size: 10px;")
        self.lbl_seal_summary_r = QLabel("R: —")
        self.lbl_seal_summary_r.setStyleSheet("color: #ef4444; font-size: 10px;")

        seal_grid.addWidget(self.lbl_seal_summary_l)
        seal_grid.addWidget(self.lbl_seal_summary_r)
        seal_grid.addStretch()
        s3_layout.addLayout(seal_grid)

        self.trend_chips_layout = QHBoxLayout()
        self.trend_chips_layout.setSpacing(3)
        s3_layout.addLayout(self.trend_chips_layout)
        card_layout.addWidget(sec3)

    def populate_tips(self):
        """Populate the tip selector dropdown from DatabaseManager catalog."""
        if not self.db or not hasattr(self.db, 'get_all_tips'):
            return
        try:
            tips = self.db.get_all_tips(include_unknown=True)
            self.cb_tip_selector.blockSignals(True)
            self.cb_tip_selector.clear()
            cur_idx = 0
            for i, tip in enumerate(tips):
                t_id = tip.get('id')
                name = tip.get('name', 'Unbekannt')
                icon = tip.get('icon_char', '?')
                mat = tip.get('material', '')
                mat_str = f" ({mat})" if mat else ""
                display = f"{icon} {name}{mat_str}"
                self.cb_tip_selector.addItem(display, userData=t_id)
                if t_id == self.tip_id:
                    cur_idx = i
            self.cb_tip_selector.setCurrentIndex(cur_idx)
            self.cb_tip_selector.blockSignals(False)
        except Exception:
            pass

    def _on_tip_combo_changed(self, idx):
        selected_tip_id = self.cb_tip_selector.currentData()
        if selected_tip_id is not None:
            self.tip_id = int(selected_tip_id)
            self.tip_changed.emit(self.tip_id)
            self.refresh_metrics()

    def set_active_iem(self, iem_id):
        if iem_id is not None:
            self.iem_id = int(iem_id)
            self.refresh_metrics()

    def set_active_tip(self, tip_id):
        if tip_id is not None:
            self.tip_id = int(tip_id)
            idx = self.cb_tip_selector.findData(self.tip_id)
            if idx != -1:
                self.cb_tip_selector.blockSignals(True)
                self.cb_tip_selector.setCurrentIndex(idx)
                self.cb_tip_selector.blockSignals(False)
            self.refresh_metrics()

    def update_data(self, iem_id=None, tip_id=None, freqs=None, mag_l=None, mag_r=None):
        if iem_id is not None:
            self.iem_id = int(iem_id)
        if tip_id is not None:
            self.tip_id = int(tip_id)
            idx = self.cb_tip_selector.findData(self.tip_id)
            if idx != -1:
                self.cb_tip_selector.blockSignals(True)
                self.cb_tip_selector.setCurrentIndex(idx)
                self.cb_tip_selector.blockSignals(False)
        if freqs is not None:
            self.freqs = freqs
        if mag_l is not None:
            self.mag_l = mag_l
        if mag_r is not None:
            self.mag_r = mag_r
        self.refresh_metrics()

    def refresh_metrics(self):
        """Query DB and update all sections: Helmholtz Peak, Reproducibility, and Seal History."""
        # 1. Helmholtz Resonance Peak
        peak_l = None
        peak_r = None
        if self.freqs is not None:
            if self.mag_l is not None:
                peak_l = self.detect_helmholtz_peak(self.freqs, self.mag_l)
            if self.mag_r is not None:
                peak_r = self.detect_helmholtz_peak(self.freqs, self.mag_r)

        # Fallback to historical median peak if live data not available
        if (peak_l is None or peak_r is None) and self.db and hasattr(self.db, 'get_tip_target_peak'):
            try:
                hist_peaks = self.db.get_tip_target_peak(self.iem_id, self.tip_id)
                if peak_l is None and hist_peaks.get('left') is not None:
                    peak_l = hist_peaks['left']
                if peak_r is None and hist_peaks.get('right') is not None:
                    peak_r = hist_peaks['right']
            except Exception:
                pass

        def update_peak_badge(lbl_val, badge_delta, peak_val, chan_name):
            if peak_val is not None:
                lbl_val.setText(f"{chan_name}: {int(round(peak_val)):,} Hz")
                delta_hz = peak_val - self.TARGET_HELMHOLTZ_HZ
                sign = "+" if delta_hz >= 0 else ""
                badge_delta.setText(f"Δ {sign}{int(round(delta_hz))} Hz")
                abs_d = abs(delta_hz)
                if abs_d <= 200:
                    badge_delta.setStyleSheet("background: #065f46; color: #34d399; border: 1px solid #10b981; border-radius: 3px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
                    badge_delta.setToolTip("Peak aligns closely with 8 kHz coupler target (Optimal depth).")
                elif abs_d <= 500:
                    badge_delta.setStyleSheet("background: #451a03; color: #fbbf24; border: 1px solid #f59e0b; border-radius: 3px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
                    badge_delta.setToolTip("Moderate resonance shift (Acceptable coupling).")
                else:
                    badge_delta.setStyleSheet("background: #7f1d1d; color: #f87171; border: 1px solid #ef4444; border-radius: 3px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
                    badge_delta.setToolTip("Resonance peak shifted > 500 Hz (Check insertion depth / seal).")
            else:
                lbl_val.setText(f"{chan_name}: — Hz")
                badge_delta.setText("—")
                badge_delta.setStyleSheet("background: #27272a; color: #71717a; border-radius: 3px; padding: 1px 4px; font-size: 9px;")
                badge_delta.setToolTip("No peak detected.")

        update_peak_badge(self.lbl_peak_l, self.badge_peak_delta_l, peak_l, "L")
        update_peak_badge(self.lbl_peak_r, self.badge_peak_delta_r, peak_r, "R")

        # 2. Reproducibility Score (Band-limited to 20-8000 Hz)
        scores = None
        count = 0
        if self.db and hasattr(self.db, 'get_reproducibility_scores'):
            try:
                scores = self.db.get_reproducibility_scores(self.iem_id, self.tip_id)
            except Exception:
                scores = None

        if scores is None:
            # Determine actual measurement count for user guidance
            if self.db and hasattr(self.db, 'db_path'):
                try:
                    import sqlite3
                    conn = sqlite3.connect(self.db.db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM Measurements WHERE iem_id = ? AND tip_id = ?", (self.iem_id, self.tip_id))
                    count = cur.fetchone()[0]
                    conn.close()
                except Exception:
                    count = 0

            self.lbl_repro_empty.setText(f"Not enough data (min. 5 measurements required, currently N={count})")
            self.lbl_repro_empty.show()
            self.repro_scores_widget.hide()
            self.badge_repro_status.hide()
        else:
            self.lbl_repro_empty.hide()
            self.repro_scores_widget.show()

            def format_score_str(sc_dict):
                if not sc_dict:
                    return "—"
                std = sc_dict.get('std_dev', sc_dict.get('score', 0.0))
                # Map std dev in dB to reproducibility percentage: 0 dB -> 100%, 0.4 dB -> 94.2%, 0.5 dB -> 92.8%
                pct = max(0.0, min(100.0, 100.0 - (std * 14.4)))
                return f"{pct:.1f}% (±{std:.1f} dB)"

            left_data = scores.get('left')
            right_data = scores.get('right')
            self.lbl_score_l.setText(f"L: {format_score_str(left_data)}")
            self.lbl_score_r.setText(f"R: {format_score_str(right_data)}")

            is_prelim = (left_data and left_data.get('is_preliminary')) or (right_data and right_data.get('is_preliminary'))
            count = (left_data.get('count') if left_data else 0) or (right_data.get('count') if right_data else 0)

            if is_prelim:
                self.badge_repro_status.setText(f"⚠ Preliminary (N={count})")
                self.badge_repro_status.setStyleSheet("background: #451a03; color: #fbbf24; border: 1px solid #f59e0b; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: bold;")
                self.badge_repro_status.setToolTip("Score is preliminary (5–9 measurements). 10+ recommended for stable statistics.")
                self.badge_repro_status.show()
            else:
                self.badge_repro_status.setText(f"✓ Stable (N={count})")
                self.badge_repro_status.setStyleSheet("background: #065f46; color: #34d399; border: 1px solid #10b981; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: bold;")
                self.badge_repro_status.setToolTip("Verified sample size (≥ 10 measurements).")
                self.badge_repro_status.show()

        # 3. Acoustic Seal History Trend (40 Hz vs 500 Hz)
        # Clear existing trend chips
        while self.trend_chips_layout.count():
            item = self.trend_chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        seal_data = {"left": [], "right": []}
        if self.db and hasattr(self.db, 'get_seal_history'):
            try:
                seal_data = self.db.get_seal_history(self.iem_id, self.tip_id) or {"left": [], "right": []}
            except Exception:
                pass

        hist_l = seal_data.get("left", [])
        hist_r = seal_data.get("right", [])

        def summarize_seal(hist, chan_name):
            n = len(hist)
            if n == 0:
                return f"{chan_name}: No takes"
            ok_cnt = sum(1 for e in hist if e.get("seal_ok"))
            pct = (ok_cnt / n) * 100.0
            mean_delta = float(np.mean([e.get("delta_db", 0.0) for e in hist]))
            return f"{chan_name}: {ok_cnt}/{n} OK ({pct:.0f}%) | Mean Δ: {mean_delta:+.1f} dB"

        self.lbl_seal_summary_l.setText(summarize_seal(hist_l, "L"))
        self.lbl_seal_summary_r.setText(summarize_seal(hist_r, "R"))

        # Render recent trend chips (up to last 8)
        recent_l = hist_l[-8:]
        for idx, entry in enumerate(recent_l):
            chip = QLabel(f"#{idx+1}")
            is_ok = entry.get("seal_ok", True)
            delta = entry.get("delta_db", 0.0)
            status = entry.get("status", "OK")
            ts = entry.get("timestamp", "")
            if is_ok:
                chip.setStyleSheet("background: #065f46; color: #34d399; border-radius: 3px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
            else:
                chip.setStyleSheet("background: #7f1d1d; color: #f87171; border-radius: 3px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
            chip.setToolTip(f"Take #{idx+1} ({ts})\nSeal Status: {status}\nDelta (40Hz vs 500Hz): {delta:+.1f} dB")
            self.trend_chips_layout.addWidget(chip)
        self.trend_chips_layout.addStretch()
```

### 4.2 Integration into `AnalysisWidget` (`analysis_ui.py`)

1. **In `AnalysisWidget.__init__`**:
   ```python
   self.tip_analysis_card = None
   self.current_iem_id = None
   self.current_tip_id = None
   ```
2. **In `AnalysisWidget.render_diagnostics()`**:
   Update line 642 guard to allow ProKit rendering even if `_last_report` is empty:
   ```python
   import config
   is_prokit = config.is_prokit_unlocked()
   if (not hasattr(self, '_last_report') or not self._last_report) and not is_prokit:
       return
   ```
   And add the card at the top of `self.report_layout`:
   ```python
   if is_prokit and (active_cat is None or active_cat == 'FR'):
       db = getattr(self, 'db', None)
       if db is None and hasattr(self, 'main_window') and hasattr(self.main_window, 'db'):
           db = self.main_window.db
       
       iem_id = getattr(self, 'current_iem_id', None)
       if iem_id is None and hasattr(self, 'main_window') and hasattr(self.main_window, 'current_iem_id'):
           iem_id = self.main_window.current_iem_id
       if iem_id is None:
           iem_id = 1

       tip_id = getattr(self, 'current_tip_id', None)
       if tip_id is None and hasattr(self, 'main_window') and hasattr(self.main_window, 'combo_tip'):
           tip_id = self.main_window.combo_tip.currentData()
       if tip_id is None:
           tip_id = 1

       self.tip_analysis_card = TipAnalysisCardWidget(
           parent=self.report_container,
           db=db,
           iem_id=iem_id,
           tip_id=tip_id,
           freqs=getattr(self, 'current_freqs', None),
           mag_l=getattr(self, 'current_mag_l', None),
           mag_r=getattr(self, 'current_mag_r', None)
       )
       # Connect sync with main_window tip selector if present
       if hasattr(self, 'main_window') and hasattr(self.main_window, 'combo_tip'):
           def sync_main_tip(t_id):
               self.current_tip_id = t_id
               idx = self.main_window.combo_tip.findData(t_id)
               if idx != -1:
                   self.main_window.combo_tip.blockSignals(True)
                   self.main_window.combo_tip.setCurrentIndex(idx)
                   self.main_window.combo_tip.blockSignals(False)
           self.tip_analysis_card.tip_changed.connect(sync_main_tip)

       self.report_layout.addWidget(self.tip_analysis_card)
   ```
3. **Add `update_prokit_visibility()` method on `AnalysisWidget`**:
   ```python
   def update_prokit_visibility(self):
       """Re-evaluates ProKit card visibility upon license state transitions."""
       import config
       unlocked = config.is_prokit_unlocked()
       if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
           self.tip_analysis_card.setVisible(unlocked)
       self.render_diagnostics()
   ```

---

## 5. Verification Method

To independently verify the implementation:

1. **Smoke Test Execution**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   *Expected*: 19/19 checks pass.
2. **E2E Diagnostics Test Suite**:
   ```bash
   pytest /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py -k "Diagnostics" -v
   ```
   *Expected*: All 11 diagnostics test cases pass.
3. **Card Visibility Gate Check**:
   ```bash
   QT_QPA_PLATFORM=offscreen python3 -c "
   import config
   from analysis_ui import TipAnalysisCardWidget
   config.revoke_prokit()
   card = TipAnalysisCardWidget()
   assert card.isVisible() is False
   config.unlock_prokit('SNITCH-PROKIT-2024-001')
   card.setVisible(config.is_prokit_unlocked())
   assert card.isVisible() is True
   config.revoke_prokit()
   print('Visibility gate verified successfully.')
   "
   ```
4. **Empty State & Warning Badge Boundary Check**:
   ```bash
   QT_QPA_PLATFORM=offscreen python3 -c "
   import tempfile, os, numpy as np
   from database import DatabaseManager
   from analysis_ui import TipAnalysisCardWidget

   with tempfile.TemporaryDirectory() as tmpdir:
       db = DatabaseManager(os.path.join(tmpdir, 'test.db'))
       f = np.linspace(20, 24000, 24001)
       p = np.zeros_like(f)
       m = np.full_like(f, 80.0)
       for _ in range(3):
           db.save_measurement(1, f, m, m, p, p, tip_id=3)
       w = TipAnalysisCardWidget(db=db, iem_id=1, tip_id=3)
       assert 'min. 5 measurements' in w.lbl_repro_empty.text()
       for _ in range(4):
           db.save_measurement(1, f, m, m, p, p, tip_id=3)
       w.setVisible(True)
       w.refresh_metrics()
       assert w.badge_repro_status.isVisible() is True
       assert 'Preliminary' in w.badge_repro_status.text()
       for _ in range(5):
           db.save_measurement(1, f, m, m, p, p, tip_id=3)
       w.refresh_metrics()
       assert w.badge_repro_status.isVisible() is True
       assert 'Stable' in w.badge_repro_status.text()
       print('Boundaries verified successfully.')
   "
   ```
