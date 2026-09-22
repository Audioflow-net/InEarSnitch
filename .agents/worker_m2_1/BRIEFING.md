# BRIEFING — 2026-09-22T08:53:01+02:00

## Mission
Implement ProKit tip-tracking database schema, migrations, seed profiles, and analytical queries (reproducibility and seal history) in `database.py`.

## 🔒 My Identity
- Archetype: worker_m2_1
- Roles: implementer, qa
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/worker_m2_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: M2 ProKit Tip-Tracking Database Implementation

## 🔒 Key Constraints
- DO NOT CHEAT. Genuine implementations only.
- Freitext is FORBIDDEN: all tip profiles live in `TipProfiles`.
- L and R channels ALWAYS separate (never averaged/combined).
- Legacy measurements (`tip_id = NULL`) automatically backfilled to "Unbekannt" (`id=1`).
- Depth-drift detection during sweep is physically impossible; do not implement.
- Reproducibility score strictly band-limited to 20 Hz – 8 kHz (`np.interp` on 20–8000 Hz, with pre-filtering `f <= 8000.0`).
- Reproducibility requires >= 5 measurements (None if < 5); 5–9 shows is_preliminary=True, >=10 is_preliminary=False.
- DATABASE SAFETY CRITICAL: /Users/ben/Desktop/InEarSnitch/inearsnitch.db is production/dev DB. DO NOT MODIFY OR CORRUPT inearsnitch.db. Never call DatabaseManager() without explicit tmp_path in scratch/tests.
- Follow audiopatch-strict-protocol and workspace rules.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T08:53:01+02:00

## Task Summary
- **What to build**: TipProfiles schema, migration & legacy backfill, seed data, `save_measurement(tip_id=1)`, `get_all_tips()`, `get_last_used_tip()`, `get_reproducibility_scores()`, `get_seal_history()` in `database.py`.
- **Success criteria**: 24 target pytest tests pass, smoke_test passes 19/19, inearsnitch.db size unchanged (16379904 bytes).
- **Interface contracts**: /Users/ben/Desktop/InEarSnitch/.agents/rules/prokit_system.md and M2 explorer handoffs.
- **Code layout**: Single-file implementation in `database.py`.

## Key Decisions Made
- [TBD]

## Artifact Index
- /Users/ben/Desktop/InEarSnitch/.agents/worker_m2_1/DISPATCH.md — Assignment instructions
- /Users/ben/Desktop/InEarSnitch/.agents/worker_m2_1/progress.md — Liveness & status tracker
- /Users/ben/Desktop/InEarSnitch/.agents/worker_m2_1/handoff.md — Final handoff report

## Change Tracker
- **Files modified**: None yet
- **Build status**: Untested
- **Pending issues**: None

## Quality Status
- **Build/test result**: Not run yet
- **Lint status**: 0
- **Tests added/modified**: tests in tests/test_prokit_e2e.py to verify

## Loaded Skills
- None
