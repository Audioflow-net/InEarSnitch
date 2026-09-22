# BRIEFING — 2026-09-22T08:15:20+02:00

## Mission
Investigate the UI structure and integration points for ProKit Tip-Tracking across main.py, history_ui.py, analysis_ui.py, theme.py, and smoke_test.py.

## 🔒 My Identity
- Archetype: explorer
- Roles: UI & Analysis Explorer
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Survey UI & Analysis for ProKit Tip-Tracking

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Do not modify source code
- Files for content delivery, messages for coordination

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T08:15:20+02:00

## Investigation State
- **Explored paths**:
  - `main.py` (lines 740-790 top_bar & logo, lines 1010-1185 bottom bar control panel, lines 2897-2987 profile selection & target matching, lines 3847-3896 save_trace_to_db, lines 3601-3667 update_analysis_view)
  - `history_ui.py` (HistoryCardWidget lines 50-101, HistoryWidget lines 102-356, load_history lines 452-542)
  - `analysis_ui.py` (AnalysisWidget lines 142-375, render_diagnostics lines 622-729, refresh_view lines 730-860)
  - `theme.py` (Dark/light mode, get_color, get_global_qss, patched_set_style)
  - `smoke_test.py` (19 critical checks, all passing)
  - `ORIGINAL_REQUEST.md`, `HANDOFF_IN_EAR_SNITCH.md`, `.agents/rules/prokit_system.md`
- **Key findings**:
  - Bottom bar: `right_group` contains `rta_widget` (RTA, Depth) and `mod_capture` (RUN, sweeps). Tip combobox cleanly fits in `right_group` adjacent to `mod_capture` or between `rta_widget` and `mod_capture` inside a dedicated `tip_widget` container, toggled with `tip_widget.setVisible(is_prokit_unlocked())`.
  - Header logo: `logo = QLabel("InEar SNITCH")` in `top_bar` (line 747). Promote to `self.lbl_logo`, attach a `QObject` event filter tracking 3 clicks within 600ms to open `open_prokit_unlock_dialog()`. Completely invisible to standard users.
  - Profile switching: Centralized in `on_profile_selected(card)` (line 2897). `self.current_iem_id = card.current_iem_id` (line 2926). Triggers `self.db.get_last_used_tip(self.current_iem_id)` and pre-selects it in `self.cb_tip`.
  - Measurement saving: `save_trace_to_db()` (line 3847) calls `self.db.save_measurement()`. Pass `tip_id=self.cb_tip.currentData()` (default 1).
  - Smoke test: 9 critical widget assignments (`self.btn_capture`, `self.btn_trace`, `self.btn_save_db`, `self.btn_rta_raw`, `self.btn_iec_guide`, `self.cb_meas_target`, `self.cb_meas_history`, `self.plot_widget`, `self.page_ana`) and 4 data flow variables must NEVER be altered.
  - History cards: `load_history()` SQL LEFT JOIN with `TipProfiles` (m.tip_id = t.id). Tip badge rendered with `icon_char` and `color_hex` (subtle grey `?` for Unbekannt). Seal status calculated from BLOBs at 40Hz vs 500Hz for Left and Right separately.
  - Analysis diagnostics: `render_diagnostics()` renders Tip Analysis card under FR tab when `is_prokit_unlocked()` is True. 8kHz peak identified via `np.argmax` over 6000–10000 Hz. Reproducibility score band-limited to 20–8000 Hz, L/R separate, None (<5) / "Not enough data", "Preliminary" warning (5–9), robust (>=10).
- **Unexplored areas**: None remaining for the assigned investigation scope.

## Key Decisions Made
- All integration points mapped with exact lines, function signatures, and UI layout specifications.

## Artifact Index
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1/DISPATCH.md — Incoming dispatch message
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1/BRIEFING.md — Persistent memory index
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1/progress.md — Liveness heartbeat
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1/handoff.md — Final technical handoff report
