# BRIEFING — 2026-09-22T07:08:30Z

## Mission
Investigate measurement saving flow, profile switching tip auto-suggestion, and ProKit lock/unlock safety in main.py for Milestone 3, producing drop-in code specifications for the Worker.

## 🔒 My Identity
- Archetype: explorer
- Roles: M3 Data Flow & Safety Explorer
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_3
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 3 (R3 main.py)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Inspect measurement saving flow in main.py
- Inspect profile switching & auto-suggestion logic
- Review test requirements in tests/test_prokit_e2e.py
- Prepare drop-in code snippets for Worker
- All outputs in .agents/explorer_m3_3/

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:08:30Z

## Investigation State
- **Explored paths**:
  - `main.py`: lines 66-70 (imports), 634-695 (`MainWindow.__init__`), 740-755 (`setup_ui` logo), 1010-1185 (`control_panel` and toolbar layout), 2720-2763 (`force_profile_selection`), 2897-2965 (`on_profile_selected`), 3847-3885 (`save_trace_to_db`), 3937-3945 (entry point & missing alias).
  - `database.py`: lines 55-148 (`TipProfiles`, migration, `save_measurement`), 174-219 (`get_all_tips`, `get_last_used_tip`).
  - `smoke_test.py`: 19/19 checks, widget and anti-regression constraints.
  - `tests/test_prokit_e2e.py`: Tier 1, 2, 3, 4 tests covering UI selector, triple-click unlock, auto-suggestion, and lifecycle toggles.
- **Key findings**:
  - Missing `InEarSnitchApp = MainWindow` alias in `main.py` caused `AttributeError: module 'main' has no attribute 'InEarSnitchApp'`.
  - `save_trace_to_db` currently calls `self.db.save_measurement(..., "")` without `tip_id`. Must retrieve `self.combo_tip.currentData()` safely guarded with `config.is_prokit_unlocked()` and fallback to `1`.
  - Profile switching occurs in `on_profile_selected` (line 2897) where `self.current_iem_id` is assigned. Auto-suggestion must query `db.get_last_used_tip(self.current_iem_id)` and fallback to id=5 (`is_default == 1`, ProKit V2).
  - Logo at line 747 needs an event filter tracking 3 clicks within 600ms to open `ProKitUnlockDialog`.
  - Bottom bar layout accommodates `self.tip_container` containing `QLabel("EAR TIP")` and `self.combo_tip` in `right_group` adjacent to RUN button.
- **Unexplored areas**: None for M3 scope.

## Key Decisions Made
- Formulate drop-in replacement snippets for Worker targeting exact line ranges in `main.py`.
- Ensure all aliases (`cb_prokit_tip`, `cb_tip`, `combo_tip`, `InEarSnitchApp`) are present for backward and test compatibility.

## Artifact Index
- DISPATCH.md — incoming dispatch instructions
- progress.md — heartbeat and progress tracker
- handoff.md — final handoff report
