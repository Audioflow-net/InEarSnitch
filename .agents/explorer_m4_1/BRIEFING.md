# BRIEFING — 2026-09-22T07:37:45Z

## Mission
Discover and document exact SQL query specifications and UI requirements for Milestone 4 (R4 history_ui.py Tip Badge integration), including schema, query design, fallback logic, widget instantiation, and test_prokit_e2e.py coverage.

## 🔒 My Identity
- Archetype: specification-miner
- Roles: M4 Spec & SQL Query Miner
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 4 (R4 history_ui.py)

## 🔒 Key Constraints
- Discover and document features by probing the authoritative specification. Do NOT implement anything.
- Prioritize authoritative sources over LLM prior knowledge.
- Be thorough but organized.
- Adhere to Teamwork protocol and handoff standards.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:37:45Z

## Task Summary
- **What to build**: Spec & SQL Query Mining for Milestone 4 (R4 history_ui.py) - LEFT JOIN TipProfiles, badge rendering, null fallback, test coverage in test_prokit_e2e.py
- **Success criteria**: Detailed analysis of current history_ui.py query, designed LEFT JOIN query, NULL handling, widget instantiation, and comprehensive review of test_prokit_e2e.py Tier 1-4 tests
- **Interface contracts**: /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- **Code layout**: /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md

## Key Decisions Made
- Confirmed current SQL query in `HistoryWidget.load_history()` lacks `m.tip_id` and does not join `TipProfiles`.
- Designed robust dual-layer `LEFT JOIN TipProfiles` query using `COALESCE` with Python-level fallback for NULL, legacy, and orphaned tip IDs.
- Extracted exact UI styling, badge text format (`"?"` for Unbekannt, `f"{icon_char} {name}"` for others), and seal status format (`"Seal: L ... | R ..."` / `"Seal L: ..."`) from `test_prokit_e2e.py`.
- Formulated complete handoff report for M4 implementation worker.

## Artifact Index
- handoff.md — Final handoff report
