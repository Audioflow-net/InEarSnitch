# BRIEFING — 2026-09-22T08:22:00+02:00

## Mission
Implement Milestone 1: R1 Offline Unlock System in `config.py`, install test suite `tests/test_prokit_gate.py`, verify all 9 unit tests and 19 smoke tests pass, and report back to parent.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 1: R1 Offline Unlock System

## 🔒 Key Constraints
- Before any code change, verify git branch is main, and run: python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
- Git backup before change: git add -A && git commit -m "backup: vor ProKit Unlock config.py"
- Write ownership: /Users/ben/Desktop/InEarSnitch/config.py and /Users/ben/Desktop/InEarSnitch/tests/test_prokit_gate.py
- VALID_CODE_HASHES: exact set of 50 SHA256 hashes from ORIGINAL_REQUEST.md
- is_prokit_unlocked() -> bool, unlock_prokit(code: str) -> bool, revoke_prokit() -> bool
- Code normalization: code.strip().upper()
- Storage: .prokit_unlocked file in get_data_dir()
- Preserve get_data_dir() and get_db_path() completely unchanged!
- Integrity: Genuine implementation, no cheating, no facade or hardcoded bypasses.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T08:22:00+02:00

## Task Summary
- **What to build**: Offline unlock system in config.py (hashes set, unlock/is_unlocked/revoke functions) + test suite in tests/test_prokit_gate.py.
- **Success criteria**: 9 unit tests passing, 19 smoke tests passing, isolated CLI check passes.
- **Interface contracts**: ORIGINAL_REQUEST.md § Milestone 1, explorer_m1_1/handoff.md, explorer_m1_2/handoff.md, explorer_m1_3/handoff.md.
- **Code layout**: config.py at repo root, tests/test_prokit_gate.py.

## Change Tracker
- **Files modified**: None yet
- **Build status**: Untested
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pending
- **Lint status**: Pending
- **Tests added/modified**: tests/test_prokit_gate.py (to be installed)

## Key Decisions Made
- Follow explorer_m1_2 implementation plan and explorer_m1_3 test suite exactly.

## Artifact Index
- /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1/DISPATCH.md — Assignment
- /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1/BRIEFING.md — Situational awareness
- /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1/progress.md — Liveness & progress tracker
