# Technical Survey Report: ProKit Tip-Tracking UI & Analysis Integration

## 1. Observation

Direct observations from inspection of `/Users/ben/Desktop/InEarSnitch/`:

### A. Baseline Smoke Test & Constraints
- Execution of `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`:
  ```
  🔍 SMOKE TEST — InEar Snitch
  1️⃣  Syntax Check (main.py, analysis_ui.py, audio_engine.py, analysis.py) -> PASS
  2️⃣  Critical Imports (PySide6, pyqtgraph) -> PASS
  3️⃣  Critical Widget References (main.py) -> PASS
  4️⃣  Data Flow & Anti-Regression (temp_mag_l, target_freqs, EQ knob anti-wrap, Card click transparency) -> PASS
  ==================================================
  ✅ ALL 19 CHECKS PASSED
  ==================================================
  ```
- From `smoke_test.py` lines 52–68, the following widget assignments in `main.py` are strictly guarded and must never be deleted or renamed:
  - `self.btn_capture =` (Line 1132)
  - `self.btn_trace =` (Line 1039)
  - `self.btn_save_db =` (Line 1045)
  - `self.btn_rta_raw =` (Line 1109)
  - `self.btn_iec_guide =` (Line 1117)
  - `self.cb_meas_target =` (Line 1058)
  - `self.cb_meas_history =` (Line 1065)
  - `self.plot_widget =` (Line 984)
  - `self.page_ana =` (Line 1193)
  - Along with data flow attributes: `self.temp_mag_l`, `self.target_freqs`, `_last_dial_val` in `analysis_ui.py`, `WA_TransparentForMouseEvents` in `main.py`, and `get_current_channel()` returning `"Left"` or `"Right"`.

### B. `main.py` UI Integration Points
1. **Bottom Bar Layout (`control_panel`)**:
   - Location: `main.py` lines 1010–1187.
   - `self.control_panel` (`QFrame`) has `control_layout = QHBoxLayout(self.control_panel)` with margins `(15, 12, 15, 12)`, spacing `20`, alignment `Qt.AlignBottom`.
   - Layout decomposition:
     - `left_group = QHBoxLayout()`: contains `mod_actions` (`btn_trace`, `btn_save_db`), `mod_compare` (`cb_meas_target`, `cb_meas_history`), and `chan_widget` (`btn_l`, `btn_r`).
     - `control_layout.addStretch()` (Line 1180).
     - `right_group = QHBoxLayout()` (spacing `7`):
       - `rta_widget` (`QVBoxLayout`, spacing 4): contains `self.btn_rta_raw` ("RTA", width 95) and `self.btn_iec_guide` ("Depth", width 95).
       - `mod_capture` (`QVBoxLayout`, spacing 4): contains `self.btn_capture` ("RUN", width 220, stretch 1) and `sweeps_widget` (width 220, segmented buttons 1x, 3x, 5x).
   - Injected into Analysis page at line 1209: `self.page_ana.layout.addLayout(bottom_container)`.

2. **Header Logo / Title Text**:
   - Location: `main.py` lines 746–753:
     ```python
     logo = QLabel("InEar SNITCH")
     logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
     sublogo = QLabel("DIAGNOSTICS")
     sublogo.setStyleSheet("color: #666; font-size: 14px; margin-left: 10px;")
     top_layout.addWidget(logo)
     top_layout.addWidget(sublogo)
     ```
   - Currently `logo` is a local variable, not assigned to `self`.

3. **Profile Switching and Current IEM ID Maintenance**:
   - In `InEarSnitchApp.__init__`: `self.current_iem_id = None` (Line 653).
   - In `MusicianCard` (lines 243–256):
     ```python
     def select_iem(self, iem_id, iem_name, btn):
         self.current_iem_id = iem_id
         self.current_iem_name = iem_name
         for b_id, b in self.avatar_btns:
             b.update_style(b_id == iem_id)
         self.iem_changed.emit()
     ```
   - In `load_profiles()` (lines 2709–2716):
     ```python
     card.iem_changed.connect(lambda c=card: self.force_profile_selection(c))
     card.mousePressEvent = make_click(card)
     ```
   - In `force_profile_selection(self, card)` (lines 2721–2756):
     Delegates directly to `self.on_profile_selected(card)`.
   - In `on_profile_selected(self, card=None)` (lines 2897–2987):
     - Line 2919: `iem_id = card.current_iem_id`
     - Line 2921: `self.current_iem_name = iem`
     - Line 2926: `self.current_iem_id = iem_id`
     - Lines 2936–2947: Auto-selects target curve based on `iem`.
     - Lines 2983–2986: Refreshes active tab (`page_prof.load_profile` or `page_hist.load_history`).

4. **Measurement Saving Flow (`save_trace_to_db`)**:
   - Location: `main.py` lines 3847–3896.
   - Connected to: `self.btn_save_db.clicked` (Line 1049) and `Ctrl+S` / `Cmd+S` shortcuts (Lines 683–684).
   - Calling code (lines 3858–3868):
     ```python
     self.db.save_measurement(
         self.current_iem_id, 
         self.temp_freqs, 
         self.temp_mag_l, 
         self.temp_mag_r, 
         self.temp_phase_l, 
         self.temp_phase_r,
         gain,
         notes,
         ""
     )
     ```
   - Signature in `database.py` line 86:
     ```python
     def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path=""):
     ```

### C. `history_ui.py`
1. **Card and List Widget Architecture**:
   - `HistoryCardWidget` (lines 50–101):
     `__init__(self, timestamp, iem_name, side, parent=None)`
     Contains `lbl_iem`, `lbl_date`, `lbl_side` (Left: `#3b82f6`, Right: `#ef4444`, Stereo: `#10b981`), and `cb_graph` (QCheckBox).
   - `HistoryWidget` (lines 102–356):
     Right pane contains `tools_tabs` with tab "ARCHIVE", containing `self.search_bar` and `self.list_widget` (`QListWidget`). Width constrained to `220`–`345` px.

2. **Loading History (`load_history`)**:
   - Location: lines 452–542.
   - Query (lines 479–485):
     ```sql
     SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name, m.meas_name
     FROM Measurements m
     JOIN IEM_Models iem ON m.iem_id = iem.id
     WHERE iem.musician_id = ?
     ORDER BY m.timestamp DESC LIMIT 100
     ```
   - BLOB parsing:
     `freq = np.frombuffer(freq_blob, dtype=np.float64)`
     `mag_l = np.frombuffer(mag_l_blob, dtype=np.float64)`
     `mag_r = np.frombuffer(mag_r_blob, dtype=np.float64)`
   - Populates `QListWidgetItem` with `data_dict` and attaches `HistoryCardWidget`.

### D. `analysis_ui.py`
1. **Layout & Diagnostics**:
   - Right pane: `self.tools_tabs` (`StableTabWidget`, width 220–400 px), Tab 0 is "Diagnostics" containing `self.report_scroll` and `self.report_layout` (`QVBoxLayout`).
   - `render_diagnostics()` (lines 622–729):
     - Takes `self._last_report` (populated in `refresh_view()`, line 850).
     - Filters by active graph tab (`tab_idx`: 0 = 'FR', 1 = 'THD', 2 = 'CSD').
     - Uses `theme.is_light()` to select card background and border colors for `'OK'`, `'WARN'`, `'FAIL'`.
     - Organizes items into `left_items` ("LEFT EAR", `#3b82f6`), `right_items` ("RIGHT EAR", `#ef4444`), and `gen_items` ("STEREO / GENERAL", `#10b981`).
     - Renders `QFrame` cards with left border accent, bold header, and `AutoWrapLabel` description.

2. **Data & Database Access in `AnalysisWidget`**:
   - Currently `AnalysisWidget` does not import `database` or instantiate a `DatabaseManager`.
   - In `main.py` line 1194, `self.page_ana.main_window = self` dynamically attaches the main window reference to `self.page_ana`.
   - `self.main_window.db` is an instance of `DatabaseManager()`.
   - `self.main_window.current_iem_id` provides the selected IEM ID.

---

## 2. Logic Chain

### A. Bottom Bar Tip Selector (`main.py`)
1. **Observation**: `right_group` contains `rta_widget` and `mod_capture` (width 220).
2. **Reasoning**:
   - The tip combobox must be placed near the RUN button without compressing or distorting `btn_capture` (which has `font-size: 24px` and height expanding).
   - Creating a dedicated container `self.tip_widget = QWidget()` placed in `right_group` between `rta_widget` and `mod_capture` (or immediately before `rta_widget`) provides a clean 130–150px wide module.
   - `self.tip_widget` contains:
     - `create_group_label("EAR TIP")` (matching the uppercase 10px bold style used elsewhere in the toolbar).
     - `self.cb_tip = QComboBox()` with `self.cb_tip.setEditable(False)` (fulfilling Design Decision 1: Freitext is strictly forbidden).
   - Visibility condition:
     ```python
     from config import is_prokit_unlocked
     self.tip_widget.setVisible(is_prokit_unlocked())
     ```
   - When locked, `self.tip_widget.setVisible(False)` collapses the widget completely with zero visual footprint. When unlocked, it renders seamlessly beside the capture block.

### B. App Logo Triple-Click Event Filter (`main.py`)
1. **Observation**: `logo = QLabel("InEar SNITCH")` is in `top_bar` (line 747).
2. **Reasoning**:
   - To make it an invisible easter egg for normal users:
     - Keep cursor as default arrow (`logo.setCursor(Qt.ArrowCursor)`).
     - Do not add any hover borders or buttons.
     - Store reference: `self.lbl_logo = logo`.
   - Qt mouse event semantics:
     A triple-click generates `MouseButtonPress` (1), `MouseButtonDblClick` (2), `MouseButtonPress` (3).
   - Installing a `QObject` event filter `ProKitUnlockFilter` on `self.lbl_logo`:
     - Tracks left clicks within a sliding `QTimer` window of 600 ms.
     - When `click_count >= 3`, stops timer, resets count, and calls `self.open_prokit_unlock_dialog()`.
   - The dialog (`QDialog`):
     - Displays license input (`QLineEdit`).
     - Calls `unlock_prokit(code)` from `config.py`.
     - If True: persists `.prokit_unlocked`, notifies user via `QMessageBox.information`, updates `self.tip_widget.setVisible(True)`, reloads tip list into `self.cb_tip`, and triggers `get_last_used_tip(self.current_iem_id)`.
     - If False: displays error message via `QMessageBox.warning`.
     - If already unlocked: provides a "Revoke / Deactivate" option calling `revoke_prokit()` and hiding `self.tip_widget`.

### C. Profile Switching & Last-Used Tip Suggestion (`main.py`)
1. **Observation**: Profile switching is executed in `on_profile_selected(self, card=None)` (lines 2897–2987), where `self.current_iem_id = card.current_iem_id`.
2. **Reasoning**:
   - `on_profile_selected()` is the single central choke point triggered by card clicks, avatar clicks, and programmatic selections.
   - Immediately following target curve auto-matching (line 2947):
     ```python
     if is_prokit_unlocked() and hasattr(self, 'cb_tip') and self.current_iem_id:
         last_tip_id = self.db.get_last_used_tip(self.current_iem_id)
         if last_tip_id is not None:
             idx = self.cb_tip.findData(last_tip_id)
             if idx >= 0:
                 self.cb_tip.setCurrentIndex(idx)
         else:
             # Default to "Unbekannt" (id=1)
             idx = self.cb_tip.findData(1)
             if idx >= 0:
                 self.cb_tip.setCurrentIndex(idx)
     ```
   - Note: Per Requirement R2, `get_last_used_tip(iem_id)` must exclude `tip_id = 1` ("Unbekannt"). If the IEM only has legacy/unknown measurements, it returns `None`, so `cb_tip` defaults to index 0 or `tip_id = 1`.

### D. Measurement Saving Flow (`main.py`)
1. **Observation**: `save_trace_to_db()` (line 3847) calls `self.db.save_measurement(...)`.
2. **Reasoning**:
   - Extract the selected tip from `self.cb_tip`:
     ```python
     tip_id = 1
     if is_prokit_unlocked() and hasattr(self, 'cb_tip'):
         selected_data = self.cb_tip.currentData()
         if selected_data is not None:
             tip_id = int(selected_data)
     ```
   - Pass `tip_id=tip_id` into `self.db.save_measurement(...)`:
     ```python
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
     ```
   - Line 3884 already refreshes history: `self.page_hist.load_history(self.active_card.m_id)`, which will immediately render the new measurement with its colored tip badge.

### E. Tip Badge & Seal Status in History Cards (`history_ui.py`)
1. **Observation**: `load_history()` queries `Measurements JOIN IEM_Models` and parses `freq_blob`, `mag_l_blob`, `mag_r_blob`.
2. **Reasoning**:
   - Update SQL query in `load_history()` to `LEFT JOIN TipProfiles`:
     ```sql
     SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, 
            iem.model_name, iem.custom_name, m.meas_name,
            t.name, t.icon_char, t.color_hex, t.material
     FROM Measurements m
     JOIN IEM_Models iem ON m.iem_id = iem.id
     LEFT JOIN TipProfiles t ON m.tip_id = t.id
     WHERE iem.musician_id = ?
     ORDER BY m.timestamp DESC LIMIT 100
     ```
   - If `t.name` is NULL (unmigrated row or `tip_id` null), fallback to: `name="Unbekannt"`, `icon_char="?"`, `color_hex="#888888"`.
   - Calculate seal values (40 Hz vs 500 Hz) directly from parsed float arrays:
     ```python
     seal_l = None
     seal_r = None
     if freq is not None and len(freq) > 0:
         idx_40 = (np.abs(freq - 40.0)).argmin()
         idx_500 = (np.abs(freq - 500.0)).argmin()
         if mag_l is not None and len(mag_l) > idx_500:
             seal_l = float(mag_l[idx_40] - mag_l[idx_500])
         if mag_r is not None and len(mag_r) > idx_500:
             seal_r = float(mag_r[idx_40] - mag_r[idx_500])
     ```
   - In `HistoryCardWidget`:
     - If `is_prokit_unlocked()`:
       - Colored Tip Badge:
         A `QLabel` displaying `f"{icon_char}"` (or `f"{icon_char} {tip_name}"`).
         For "Unbekannt" (id=1): subtle dark grey badge `background-color: #3f3f46; color: #a1a1aa; border: 1px solid #52525b;`.
         For registered tips: `background-color: {color_hex}; color: white; border-radius: 4px; padding: 2px 5px; font-size: 10px; font-weight: bold;`.
         Set tooltip: `f"Ear Tip: {tip_name} ({material})"`.
       - L and R Seal Status:
         Format string separately for L and R:
         If both: `f"Seal: L {seal_l:+.1f}dB | R {seal_r:+.1f}dB"`
         If Left only: `f"Seal L: {seal_l:+.1f}dB"`
         If Right only: `f"Seal R: {seal_r:+.1f}dB"`
         Displayed as a secondary metadata label beneath `lbl_date` in `info_layout`.
     - If locked:
       Neither badge nor seal status are rendered.

### F. Tip Analysis in Diagnostics (`analysis_ui.py`)
1. **Observation**: Diagnostics are rendered by `render_diagnostics()` within `self.report_layout`. Each card is a styled `QFrame` with a colored status border.
2. **Reasoning**:
   - When `is_prokit_unlocked()` is True and active tab is FR (`tab_idx == 0` or `active_cat == 'FR'`), inject a dedicated Tip Analysis section.
   - Access to database and state:
     - `iem_id = self.main_window.current_iem_id if hasattr(self, 'main_window') else None`
     - `tip_id = self.main_window.cb_tip.currentData() if (hasattr(self, 'main_window') and hasattr(self.main_window, 'cb_tip')) else 1`
     - `db = self.main_window.db if hasattr(self, 'main_window') else DatabaseManager()`
   - **8 kHz Target Peak Detection**:
     - From current measurement arrays `freqs`, `mag_l`, `mag_r`:
       ```python
       mask = (freqs >= 6000) & (freqs <= 10000)
       if np.any(mask):
           sub_f = freqs[mask]
           if mag_l is not None:
               sub_ml = mag_l[mask]
               peak_idx_l = np.argmax(sub_ml)
               peak_f_l = sub_f[peak_idx_l]
               peak_m_l = sub_ml[peak_idx_l]
           if mag_r is not None:
               sub_mr = mag_r[mask]
               peak_idx_r = np.argmax(sub_mr)
               peak_f_r = sub_f[peak_idx_r]
               peak_m_r = sub_mr[peak_idx_r]
       ```
     - Compares detected peak frequency to nominal 8000 Hz reference plane:
       `L Peak: {peak_f_l:,.0f} Hz ({peak_m_l:.1f} dB SPL) — Delta: {peak_f_l - 8000:+d} Hz`
       `R Peak: {peak_f_r:,.0f} Hz ({peak_m_r:.1f} dB SPL) — Delta: {peak_f_r - 8000:+d} Hz`
   - **Reproducibility Score**:
     - Query `db.get_reproducibility_scores(iem_id, tip_id)`:
       Calculates std dev over 20 Hz – 8000 Hz, L and R separate.
       If count < 5: returns `(None, None, count)`.
       UI shows: `"Not enough data (min. 5 measurements required, currently N={count})"`, status: `WARN`.
       If 5 <= count < 10:
       UI shows: `"Preliminary score (N={count} < 10): Left ±{score_l:.2f} dB | Right ±{score_r:.2f} dB (20 Hz – 8 kHz)"`, status: `WARN`.
       If count >= 10:
       UI shows: `"Solid score (N={count}): Left ±{score_l:.2f} dB | Right ±{score_r:.2f} dB (20 Hz – 8 kHz)"`, status: `OK`.
   - **Seal History Trend**:
     - Query `db.get_seal_history(iem_id, tip_id)`:
       Retrieves chronological sequence of 40Hz vs 500Hz deltas for L and R.
       Calculates average and standard deviation:
       `Left: Avg {mean_l:+.1f} dB (±{std_l:.1f} dB)`
       `Right: Avg {mean_r:+.1f} dB (±{std_r:.1f} dB)`

---

## 3. Caveats

1. **Hardware-Specific Audio Sweeps**:
   During tests, audio hardware is not engaged; analysis testing relies on unmarshaling stored binary BLOBs and database mocks.
2. **Legacy DB Backfill**:
   If an existing database is loaded before migration, `tip_id` will be absent until `DatabaseManager._init_db()` executes the migration. All queries in `history_ui.py` must use `LEFT JOIN` and handle `NULL` gracefully.
3. **Coupler Resonance Boundary**:
   The 8kHz peak search window is strictly bounded to 6,000 Hz – 10,000 Hz. If an IEM has unusual damping or a secondary peak, `np.argmax` selects the highest magnitude within that window.
4. **Theme Transitions**:
   When toggling dark/light mode via `self.btn_theme`, custom-styled badges must update or use theme-agnostic readable contrast (white text on dark badge backgrounds, or classes handled by `theme.patched_set_style`).

---

## 4. Conclusion

The UI and Analysis integration points are clear, isolated, and safe:
1. **`main.py`**:
   - Add `tip_widget` with non-editable `self.cb_tip` into `right_group` adjacent to `mod_capture`. Visibility bound to `is_prokit_unlocked()`.
   - Promote `logo` to `self.lbl_logo`, attach `ProKitUnlockFilter` for triple-click activation dialog.
   - Hook last-used tip suggestion in `on_profile_selected()` via `db.get_last_used_tip(self.current_iem_id)`.
   - In `save_trace_to_db()`, extract `tip_id` from `self.cb_tip.currentData()` (default 1) and pass to `db.save_measurement()`.
   - Preserve all 9 critical smoke-test widgets without renaming or structural breaking.
2. **`history_ui.py`**:
   - Update `load_history()` SQL to `LEFT JOIN TipProfiles`.
   - Calculate seal values (40Hz vs 500Hz) from BLOBs.
   - Render colored tip badges and separate L/R seal status on `HistoryCardWidget` when unlocked.
3. **`analysis_ui.py`**:
   - In `render_diagnostics()`, add Tip Analysis card under FR tab when unlocked.
   - Peak search over 6–10 kHz from measurement BLOBs.
   - Reproducibility score band-limited to 20–8000 Hz with strict `<5` and `<10` threshold handling and separate L/R channels.

---

## 5. Verification Method

To independently verify the architecture and integration:

1. **Run Smoke Test (Integrity Baseline)**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   Must pass 19/19 checks with exit code 0.

2. **Inspect Integration Points**:
   - `main.py`: Verify lines 747 (`logo`), 1010–1185 (`control_panel` and `right_group`), 2919–2926 (`on_profile_selected`), and 3847–3868 (`save_trace_to_db`).
   - `history_ui.py`: Verify lines 50–101 (`HistoryCardWidget`) and 479–535 (`load_history`).
   - `analysis_ui.py`: Verify lines 622–729 (`render_diagnostics`) and 850 (`_last_report`).

3. **Behavioral Invalidation Conditions**:
   - If `self.btn_capture` or any other critical widget from `smoke_test.py` is renamed or deleted -> `smoke_test.py` fails immediately.
   - If `cb_tip` allows freetext -> Violation of Design Decision 1.
   - If L and R reproducibility scores or seal deltas are combined into a single value -> Violation of Design Decision 2.
   - If reproducibility is evaluated above 8000 Hz -> Violation of Design Decision 5.
   - If reproducibility returns a score with <5 measurements -> Violation of Design Decision 6.
   - If any ProKit element is visible when `.prokit_unlocked` does not exist -> Violation of Requirement R1/Gate-Pattern.
