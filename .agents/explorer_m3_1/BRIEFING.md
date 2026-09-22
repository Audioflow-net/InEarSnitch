# BRIEFING — 2026-09-22T09:03:55+02:00

## Mission
Discover and document UI layout, combo_tip placement, widget safety, and e2e test requirements for Milestone 3 (main.py ProKit integration).

## 🔒 My Identity
- Archetype: specification_miner
- Roles: Teamwork specialist, external domain expert
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 3 (R3 main.py UI Layout & Integration)

## 🔒 Key Constraints
- Do NOT implement anything — read-only spec and layout mining.
- 9 critical widget references in smoke_test.py must remain untouched: combo_musician, combo_iem, btn_capture, input_gain, btn_toggle_phase, btn_undo, btn_redo, btn_auto_scale, theme_selector.
- combo_tip must be QComboBox with setEditable(False) (Freitext strictly forbidden).
- ProKit UI visibility controlled by config.is_prokit_unlocked().
- Default selection logic: select tip with is_default == 1 (ProKit V2, id=5).
- Follow all audiopatch-strict-protocol and workspace rules.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: not yet

## Task Summary
- **What to build**: Specification mining report for Milestone 3 (R3 main.py) UI layout, tip selector placement, population, visibility, smoke_test safety, and test_prokit_e2e requirements.
- **Success criteria**: Comprehensive handoff report in `.agents/explorer_m3_1/handoff.md` with complete observation, logic chain, caveats, conclusion, and verification method; parent notified.
- **Interface contracts**: /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md, /Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
- **Code layout**: /Users/ben/Desktop/InEarSnitch/main.py

## Key Decisions Made
- Investigated main.py, smoke_test.py, test_prokit_e2e.py, ORIGINAL_REQUEST.md, PROJECT.md.
- Bottom bar layout identified: self.control_panel -> control_layout -> right_group (between rta_widget and mod_capture).
- combo_tip designed with self.tip_container, setEditable(False), objectName("cb_prokit_tip"), alias cb_tip.
- Population logic designed: DatabaseManager.get_all_tips() with display text f"{icon_char} {name}" and userData=tip['id'].
- Default tip selection logic: is_default == 1 (id=5, ProKit V2).
- Auto-suggest logic designed: on_profile_selected() calls db.get_last_used_tip(iem_id); falls back to id=5 if None.
- Persistence designed: save_trace_to_db() forwards active tip_id to db.save_measurement().
- Verified 9 critical widget references in smoke_test.py (self.btn_capture, self.btn_trace, self.btn_save_db, self.btn_rta_raw, self.btn_iec_guide, self.cb_meas_target, self.cb_meas_history, self.plot_widget, self.page_ana).
- Identified InEarSnitchApp = MainWindow module alias requirement to satisfy E2E test harness.
- Completed handoff report in .agents/explorer_m3_1/handoff.md.

## Artifact Index
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1/handoff.md — Spec mining handoff report
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1/progress.md — Liveness heartbeat
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1/DISPATCH.md — Received dispatch records
