# BRIEFING — 2026-09-22T07:10:00Z

## Mission
Implement ProKit Tip-Tracking UI in InEarSnitch `main.py` (tip selector, triple-click unlock, persistence, profile restore, smoke & test suite compliance).

## 🔒 My Identity
- Archetype: M3 UI Worker
- Roles: implementer, qa, specialist
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/worker_m3_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: M3 (UI & Integration)

## 🔒 Key Constraints
- Exclusive write ownership: ONLY edit `/Users/ben/Desktop/InEarSnitch/main.py` (and worker files in `.agents/worker_m3_1/`).
- Freitext is FORBIDDEN: `combo_tip` MUST NOT be editable (`combo_tip.setEditable(False)`).
- L and R channels ALWAYS separate.
- tip_id = 1 for Unbekannt.
- DO NOT rename, remove, or break any critical widget checked by `smoke_test.py`:
  `combo_musician`, `combo_iem`, `btn_capture`, `input_gain`, `btn_toggle_phase`, `btn_undo`, `btn_redo`, `btn_auto_scale`, `theme_selector`.
- Keep `stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db` untouched (16379904 bytes).

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:10:00Z

## Task Summary
- **What to build**: Tip selector UI (`combo_tip`/`cb_tip`, `tip_container`), logo triple-click filter for ProKit unlock dialog, profile switching tip restore, `save_trace_to_db` tip_id propagation, module-level alias `InEarSnitchApp = MainWindow`.
- **Success criteria**: All targeted tests in `test_prokit_e2e.py` pass; `smoke_test.py` passes 19/19; DB size untouched.
- **Interface contracts**: `database.py` (get_all_tips, get_last_used_tip, save_measurement), `config.py` (is_prokit_unlocked, unlock_prokit).
- **Code layout**: All changes in `/Users/ben/Desktop/InEarSnitch/main.py`.

## Change Tracker
- **Files modified**: None yet
- **Build status**: Untested
- **Pending issues**: None

## Quality Status
- **Build/test result**: Not yet run
- **Lint status**: Clean
- **Tests added/modified**: None (using existing test suites)

## Loaded Skills
- None

## Key Decisions Made
- Follow explorer handoffs for exact implementation patterns.

## Artifact Index
- `/Users/ben/Desktop/InEarSnitch/.agents/worker_m3_1/DISPATCH.md` — Assignment
- `/Users/ben/Desktop/InEarSnitch/.agents/worker_m3_1/progress.md` — Liveness & progress tracking
