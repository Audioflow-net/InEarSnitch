# BRIEFING — 2026-09-22T08:10:40+02:00

## Mission
Survey and extract the exhaustive specification for ProKit Tip-Tracking from authoritative sources.

## 🔒 My Identity
- Archetype: Teamwork specialist / Specification Miner
- Roles: Specification Miner
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: ProKit Tip-Tracking Spec Survey

## 🔒 Key Constraints
- Freetext forbidden for tips (dropdown only)
- L/R separate tracking
- Legacy tip_id=1 Unbekannt (always seeded first)
- Depth-drift detection impossible (must clearly state reasons: no baseline, geometry shifts)
- 20Hz-8kHz band-limited reproducibility score (std dev 20Hz-8kHz, L/R separate, >=5 threshold, preliminary warning 5-9)
- Live features guard: never break existing measurement, audio, or analysis pipelines
- Read-only miner: do NOT implement anything

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: not yet

## Task Summary
- **What to build/extract**: Exhaustive specification for ProKit Tip-Tracking across config.py (R1), database.py (R2), main.py (R3), history_ui.py (R4), and analysis_ui.py (R5), plus locked design decisions, edge cases, acceptance criteria, and anti-regression constraints.
- **Success criteria**: Complete handoff.md with 5 components covering all 7 survey requirements with verbatim details, hash values, queries, signatures, and formulas.
- **Interface contracts**: ORIGINAL_REQUEST.md, rules/prokit_system.md, rules/live_features_guard.md, HANDOFF_IN_EAR_SNITCH.md
- **Code layout**: /Users/ben/Desktop/InEarSnitch/

## Loaded Skills
- None specified in prompt

## Key Decisions Made
- Prioritize authoritative source documents: ORIGINAL_REQUEST.md, rules/prokit_system.md, rules/live_features_guard.md, HANDOFF_IN_EAR_SNITCH.md, and codebase files.
- Completed comprehensive spec mining across all 7 required survey domains (R1-R5, locked decisions, acceptance checklist).
- Verified exact 50 SHA256 hashes matching SNITCH-PROKIT-2024-001..050 with 100% precision.
- Verified database state (9 legacy measurements ready for tip_id=1 migration).
- Verified baseline smoke test (19/19 passing).

## Artifact Index
- /Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1/handoff.md — Final specification mining handoff report
- /Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1/progress.md — Liveness heartbeat and progress log
- /Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1/DISPATCH.md — Original dispatch assignment

