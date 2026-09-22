# BRIEFING — 2026-09-22T07:48:00Z

## Mission
Implement Milestone 4 (R4 history_ui.py): Refactor HistoryCardWidget and HistoryWidget for ProKit Tip Badges and Acoustic Seal display, maintaining backward compatibility and strict database safety.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/worker_m4_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: M4 (history_ui.py)

## 🔒 Key Constraints
- Exclusive write ownership: ONLY `/Users/ben/Desktop/InEarSnitch/history_ui.py`. Do NOT touch any other source file.
- Before code edit: run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (must pass).
- Before code edit: git commit snapshot: `git add -A && git commit -m "backup: vor ProKit history_ui.py"`.
- Database safety: `inearsnitch.db` MUST remain EXACTLY 16379904 bytes. Never write to inearsnitch.db.
- Must satisfy all ProKit gating, Locked Design Decision 2 (L and R separate seal), badge formatting, aliases, and SQL joins.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:48:00Z

## Task Summary
- **What to build**: Tip badges and acoustic seal in HistoryCardWidget and HistoryWidget
- **Success criteria**: Smoke test passes (19/19), pytest History tests pass, DB size unchanged (16379904 bytes)
- **Interface contracts**: PROJECT.md, ORIGINAL_REQUEST.md, handoffs from explorer_m4_1/2/3

## Key Decisions Made
- `HistoryCardWidget` refactored with backward-compatible constructor signature accepting `tip_id`, `tip_name`, `tip_color`, `tip_icon`, `tip_material`, `seal_l`, `seal_r`, `seal_text`, `freq`, `mag_l`, `mag_r`, and `**kwargs`.
- Acoustic seal calculated via IEC-711 bass coupling delta: `mean(mag[35..45 Hz]) - mean(mag[450..550 Hz])` against threshold `-11.8 dB`.
- Locked Design Decision 2 enforced: `lbl_seal_l` and `lbl_seal_r` kept strictly separate for Left and Right channels, with formatted `lbl_seal` string.
- Tip badges styled with icon and color, subtle grey `"?"` (`#6b7280` / `#a1a1aa`) for Unbekannt/id=1, with aliases `tip_badge` and `lbl_badge`.
- `load_history` updated with `LEFT JOIN TipProfiles t ON m.tip_id = t.id` and BLOB decoding.
- `update_prokit_ui_visibility` added on `HistoryWidget` and `update_prokit_visibility` on `HistoryCardWidget`.
- Database size preserved at exactly 16379904 bytes.

## Artifact Index
- `.agents/worker_m4_1/DISPATCH.md` — assignment
- `.agents/worker_m4_1/BRIEFING.md` — working memory
- `.agents/worker_m4_1/progress.md` — liveness heartbeat
- `.agents/worker_m4_1/handoff.md` — final handoff report

## Change Tracker
- **Files modified**: `history_ui.py` (ProKit tip badges and acoustic seal in HistoryCardWidget and HistoryWidget)
- **Build status**: Passed smoke test (19/19), passed all History tests (15/15), passed adversarial suites (UI 21/21, DB 26/26, DSP 20/20)
- **Pending issues**: None

## Quality Status
- **Build/test result**: All checks passed.
- **Lint status**: Clean (py_compile passed cleanly)
- **Tests added/modified**: None (read-only test suite preserved)

## Loaded Skills
- None
