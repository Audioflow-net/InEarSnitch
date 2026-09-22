# BRIEFING — 2026-09-22T07:42:00Z

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
- Updated: 2026-09-22T07:42:00Z

## Task Summary
- **What to build**: Tip badges and acoustic seal in HistoryCardWidget and HistoryWidget
- **Success criteria**: Smoke test passes (19/19), pytest History tests pass, DB size unchanged (16379904 bytes)
- **Interface contracts**: PROJECT.md, ORIGINAL_REQUEST.md, handoffs from explorer_m4_1/2/3

## Key Decisions Made
- [TBD]

## Artifact Index
- `.agents/worker_m4_1/DISPATCH.md` — assignment
- `.agents/worker_m4_1/BRIEFING.md` — working memory
- `.agents/worker_m4_1/progress.md` — liveness heartbeat
- `.agents/worker_m4_1/handoff.md` — final handoff report

## Change Tracker
- **Files modified**: None yet
- **Build status**: Pending pre-flight
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pending
- **Lint status**: Clean
- **Tests added/modified**: None (tests are read-only)

## Loaded Skills
- None
