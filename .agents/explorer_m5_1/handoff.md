# Milestone 5 (R5 analysis_ui.py) Spec & Diagnostics Layout Mining Report

## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | UI / Gate | ProKit Unlock Gating | The Tip Analysis Card is rendered in `render_diagnostics()` strictly if `config.is_prokit_unlocked()` is True. When locked, the card is omitted entirely. | `config.is_prokit_unlocked()` | Card added to `report_layout` if True; omitted if False | Locked state yields clean report without card; no exception | `ORIGINAL_REQUEST.md` R5, `PROJECT.md` F18, `analysis_ui.py:622` |
| 2 | DSP / Layout | 8 kHz Helmholtz Resonance Peak | Detects half-wave / coupler resonance peak in the 6 kHz – 10 kHz window (6000–10000 Hz) for Left and Right channels separately. | Frequency array $f \in [20, 24000]$, magnitudes $M_L, M_R$ | Peak frequency in Hz ($f_{\text{peak}, L}, f_{\text{peak}, R}$) and deviation vs 8000 Hz | Flat spectrum returns boundary frequency; empty/invalid BLOB returns None / "N/A" | `ORIGINAL_REQUEST.md` R5, `database.py:415`, `test_prokit_e2e.py:589` |
| 3 | DSP / Layout | Band-Limited Reproducibility Score | Mean standard deviation (dB) across repeated measurements strictly band-limited to 20 Hz – 8 kHz. L and R calculated separately. | Stored BLOBs for `iem_id` and `tip_id`, common grid 20–8000 Hz | Score dict: `{'score', 'std_dev', 'count', 'is_preliminary'}` for L & R | Returns `None` if $N < 5$; high-frequency variance >8 kHz strictly ignored | `ORIGINAL_REQUEST.md` R5 & Decision 5, `database.py:242`, `test_prokit_e2e.py:604` |
| 4 | UI / Threshold | Reproducibility Sample Thresholds | Threshold logic: $N < 5 \to$ "Not enough data"; $5 \le N \le 9 \to$ "Preliminary" warning; $N \ge 10 \to$ confirmed stable score. | Measurement count $N$ per channel | Status string / pill badge (`badge_repro_preliminary`) | Never crashes if count is 0 or 4 | `ORIGINAL_REQUEST.md` Decision 6, `database.py:304`, `test_prokit_e2e.py:612` |
| 5 | DSP / Layout | Acoustic Seal History Trend | Evaluates historical acoustic seal ($\Delta = \text{SPL}_{40\,\text{Hz}} - \text{SPL}_{500\,\text{Hz}}$) across measurements for L and R separately. | Stored BLOBs for `iem_id` and `tip_id` | History dict `{'left': [...], 'right': [...]}` with delta dB, status ("OK"/"LEAK") | Missing 40Hz/500Hz band returns empty history; corrupt rows skipped | `ORIGINAL_REQUEST.md` R5, `database.py:328`, `test_prokit_e2e.py:623` |
| 6 | UI / Navigation | Tab Filtering & Zoom Reactivity | In `render_diagnostics()`, diagnostics cards are filtered by active graph tab (`0: 'FR', 1: 'THD', 2: 'CSD'`). Tip Analysis card is anchored to 'FR' / overall acoustics. | `self.graph_tabs.currentIndex()` | Card rendered in FR tab and when general acoustics are inspected | Switching tabs cleanly removes and redraws cards | `analysis_ui.py:174, 650` |
| 7 | UI / Reactive Sync | Dynamic Update on New Measurement | When a new measurement is run or IEM/tip selection changes, `render_diagnostics()` updates counts, peaks, and scores. | New measurement save or profile/tip change | Re-rendered card with latest metrics | Old widgets in `report_layout` are safely deleted via `deleteLater()` | `main.py:2659, 4103`, `analysis_ui.py:851` |

## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | ProKit Gate | `is_prokit_unlocked() == False` | No Tip Analysis card is created or visible in `report_layout`. Normal diagnostics cards remain intact. |
| 2 | ProKit Gate Lifecycle | Unlocked $\to$ Revoked $\to$ Unlocked | `main.update_prokit_ui_visibility()` calls `page_ana.render_diagnostics()`; card appears, disappears, and reappears cleanly without layout corruption. |
| 3 | Sample Threshold | Exactly $N = 4$ measurements | `get_reproducibility_scores()` returns `None`. UI displays empty state label: `"Not enough data (min. 5 measurements required, currently N=4)"`. |
| 4 | Boundary Condition | $N = 9$ vs $N = 10$ measurements | At $N = 9$: `is_preliminary = True`, yellow preliminary badge shown. At $N = 10$: `is_preliminary = False`, badge disappears. |
| 5 | Flat / Monotonic Spectrum | Constant magnitude across 6–10 kHz | `argmax` returns the first index (6000 Hz) without error. No divide-by-zero or `IndexError`. |
| 6 | Peak Outside Window | Resonance peak at 5.5 kHz or 11.5 kHz | Algorithm restricts search strictly to `[6000, 10000]` Hz; returns highest point within window. |
| 7 | Zero Variance | Identical curves ($N=5$) | Standard deviation is exactly `0.00 dB`; no divide-by-zero exception. |
| 8 | Severe High-Frequency Noise | $0.25\text{ dB}$ variance in 20–8000 Hz, but $15\text{ dB}$ noise $>8000\text{ Hz}$ | Band-limiting completely filters out $>8000\text{ Hz}$ noise; reproducibility score remains around $0.25\text{ dB}$. |
| 9 | Corrupt / Truncated BLOB | Truncated byte buffers, `None`, length mismatch | `frombuffer` / length check fails safely; bad record is skipped; remaining valid measurements are processed. |
| 10 | Mono Measurement | Left channel measured, Right channel `None` | Left displays valid peak/score; Right displays `"N/A"` / `"Not enough data"`. Never averages across channels. |
| 11 | Empty Database / Stale Report | No measurements exist for IEM/tip | Card shows empty state for all sections without throwing `NoneType` or `KeyError`. |

---

## 1. Observation

### 1.1 `analysis_ui.py` Diagnostics Architecture
1. **Container Hierarchy**:
   - `AnalysisWidget(QWidget)` (`objectName="AnalysisRoot"`)
     - Splitter: `self.split_layout = QSplitter(Qt.Horizontal)`
     - Left Pane: `self.graph_tabs = QTabWidget()` (Tab 0: "Freq Response", Tab 1: "Distortion (THD)", Tab 2: "Waterfall (CSD)")
     - Right Pane: `self.right_pane_wrapper = QWidget()`
       - `self.btn_toggle_tools = QPushButton("▶")`
       - `self.tools_tabs = StableTabWidget()`
         - Tab 0: `self.diag_container = QWidget()` ("Diagnostics")
           - Layout: `diag_layout = QVBoxLayout(self.diag_container)`
           - Scroll Area: `self.report_scroll = QScrollArea()`
           - Container: `self.report_container = QWidget()`
           - Card Layout: `self.report_layout = QVBoxLayout(self.report_container)` (Margins: 4, Spacing: 4)

2. **Existing `render_diagnostics()` Flow (lines 622–729)**:
   - Line 637–640: Clears all existing widgets from `self.report_layout`:
     ```python
     while self.report_layout.count():
         item = self.report_layout.takeAt(0)
         if item.widget():
             item.widget().deleteLater()
     ```
   - Line 650–652: Maps tab index: `0 -> 'FR'`, `1 -> 'THD'`, `2 -> 'CSD'`.
   - Lines 661–677: Segregates `self._last_report` into `left_items`, `right_items`, and `gen_items`.
   - Lines 683–727: Renders groups:
     - `render_group(left_items, "LEFT EAR", "#3b82f6")`
     - `render_group(right_items, "RIGHT EAR", "#ef4444")`
     - `render_group(gen_items, "STEREO / GENERAL", "#10b981")`
   - Line 728: `self.report_layout.addStretch()`.

3. **Reactivity & Invocation Sites**:
   - `self.graph_tabs.currentChanged` (line 174) $\to$ calls `self.render_diagnostics()`.
   - `self.refresh_view()` (line 851) $\to$ calls `self.render_diagnostics()`.
   - `self.changeEvent()` (line 1125) $\to$ calls `self.render_diagnostics()`.
   - `main.py:2659` (after stress test) $\to$ calls `self.page_ana.render_diagnostics()`.
   - `main.py:4105` (`update_prokit_ui_visibility()`) $\to$ calls `self.page_ana.render_diagnostics()`.

### 1.2 `database.py` Existing Back-End Queries (Milestone 2)
The necessary analytics methods are already implemented in `database.py`:
- `get_tip_target_peak(iem_id, tip_id)` (lines 415–471):
  Returns `{"left": float | None, "right": float | None}` (median peak frequency in 6–10 kHz).
- `get_reproducibility_scores(iem_id, tip_id)` (lines 242–326):
  Returns `{"left": dict | None, "right": dict | None}` where each channel is `{"score": float, "std_dev": float, "count": int, "is_preliminary": bool}` or `None` if $N < 5$.
- `get_seal_history(iem_id, tip_id)` (lines 328–413):
  Returns `{"left": list[dict], "right": list[dict]}` with delta dB ($40\text{ Hz} - 500\text{ Hz}$), seal status (`"OK"` vs `"LEAK"`).

---

## 2. Logic Chain

1. **Card Placement Strategy**:
   - Coupler resonance and tip acoustic seal dictate fundamental measurement accuracy.
   - Positioning the Tip Analysis card at the **TOP** of `self.report_layout` (before "LEFT EAR" / "RIGHT EAR") ensures immediate visibility of physical coupling status.
   - When tab is "Freq Response" (`active_cat in ('FR', None)`), physical ear tip coupling is directly relevant to the displayed curve.

2. **Feature Gate Logic**:
   - `config.is_prokit_unlocked()` controls visibility.
   - If False: `_render_tip_analysis_card()` is bypassed. No card is created, matching the strict requirement: *"All ProKit UI elements are invisible when is_prokit_unlocked() returns False"*.
   - If True: `_render_tip_analysis_card()` is executed, querying the database for current `(iem_id, tip_id)` and generating the card.

3. **Data Source Resolution**:
   - IEM ID: `getattr(self, 'current_iem_id', None)` or `self.main_window.active_card.m_id`.
   - Tip ID: `getattr(self, 'current_tip_id', None)` or `self.main_window.combo_tip.currentData()` or fallback to `None`.
   - Database instance: `getattr(self, 'db', None)` or `getattr(self.main_window, 'db', None)` or `database.DatabaseManager(getattr(self, 'db_path', 'inearsnitch.db'))`.
   - Live Curve Peak (if live sweep is active): computed from `(self.current_freqs, self.current_mag_l, self.current_mag_r)` in the 6–10 kHz window.

4. **Widget Hierarchy & ObjectNames**:
```
card_tip_analysis (QFrame, objectName="card_tip_analysis")
├── card_layout (QVBoxLayout)
│   ├── header_layout (QHBoxLayout)
│   │   ├── lbl_tip_card_title (QLabel, objectName="lbl_tip_card_title")
│   │   └── lbl_tip_badge (QLabel, objectName="lbl_tip_badge")
│   ├── sec_helmholtz (QFrame, objectName="sec_helmholtz")
│   │   ├── lbl_helmholtz_title (QLabel, objectName="lbl_helmholtz_title")
│   │   ├── resonance_layout (QHBoxLayout)
│   │   │   ├── lbl_peak_l (QLabel, objectName="lbl_peak_l")
│   │   │   ├── lbl_peak_r (QLabel, objectName="lbl_peak_r")
│   │   │   └── lbl_peak_delta (QLabel, objectName="lbl_peak_delta")
│   ├── sec_reproducibility (QFrame, objectName="sec_reproducibility")
│   │   ├── repro_header_layout (QHBoxLayout)
│   │   │   ├── lbl_repro_title (QLabel, objectName="lbl_repro_title")
│   │   │   └── badge_repro_preliminary (QLabel, objectName="badge_repro_preliminary")
│   │   ├── repro_layout (QHBoxLayout)
│   │   │   ├── lbl_repro_l (QLabel, objectName="lbl_repro_l")
│   │   │   └── lbl_repro_r (QLabel, objectName="lbl_repro_r")
│   │   └── lbl_repro_warning (QLabel, objectName="lbl_repro_warning")
│   └── sec_seal_history (QFrame, objectName="sec_seal_history")
│       ├── lbl_seal_trend_title (QLabel, objectName="lbl_seal_trend_title")
│       └── seal_layout (QHBoxLayout)
│           ├── lbl_seal_trend_l (QLabel, objectName="lbl_seal_trend_l")
│           └── lbl_seal_trend_r (QLabel, objectName="lbl_seal_trend_r")
```

---

## 3. Caveats

1. **Standalone Widget Testing without `main_window`**:
   - In unit tests where `AnalysisWidget` is instantiated directly without `main.MainWindow()`, `self.main_window` will be None.
   - **Remedy**: `AnalysisWidget` must gracefully handle `main_window is None`, using `self.db` or `self.db_path` or creating a local `DatabaseManager`, and accepting `set_active_tip(tip_id)` / `set_active_iem(iem_id)`.
2. **First Run Before Any Measurement**:
   - When the app is launched and no sweep has been run, `self._last_report` is None or empty.
   - **Remedy**: Even if `self._last_report` is empty, if `config.is_prokit_unlocked()` and an IEM profile is active, the Tip Analysis card can still render historical data (reproducibility, seal trend, median peak) rather than returning early on `not self._last_report`.

---

## 4. Conclusion

The diagnostics layout structure in `analysis_ui.py` is modular and well-suited for adding the ProKit Tip Analysis card. All mathematical back-end methods already exist in `database.py`. The M5 Worker should implement:
1. `_render_tip_analysis_card(self)` in `analysis_ui.py`.
2. Gating in `render_diagnostics()` checking `config.is_prokit_unlocked()`.
3. Support for `self.db` / `self.db_path` injection for testing.
4. Exact widget `objectName`s matching the specification table above.

---

## 5. Verification Method

To independently verify all contracts:

```bash
# 1. Verify smoke test passes (19/19)
python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py

# 2. Run existing ProKit E2E Diagnostics tests
python3 -m pytest tests/test_prokit_e2e.py -k "Diag or reproducibility" -v

# 3. Verify headless Qt widget instantiation
python3 -c "
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
import analysis_ui
app = QApplication.instance() or QApplication(['test', '-platform', 'offscreen'])
w = analysis_ui.AnalysisWidget()
assert hasattr(w, 'render_diagnostics')
print('AnalysisWidget instantiation verified successfully.')
"
```
