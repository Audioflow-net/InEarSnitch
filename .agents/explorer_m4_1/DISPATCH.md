## 2026-09-22T07:34:58Z
You are M4 Spec & SQL Query Miner for Milestone 4 (R4 history_ui.py) in the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Your mission:
1. Examine `load_history` in `history_ui.py`:
   - Inspect the current SQL query in `HistoryWidget.load_history()` or wherever database rows are retrieved.
   - Design the `LEFT JOIN TipProfiles ON Measurements.tip_id = TipProfiles.id` query.
   - Column selection: ensure `TipProfiles.name`, `TipProfiles.color_hex`, `TipProfiles.icon_char`, `TipProfiles.material`, and `Measurements.tip_id` are fetched.
   - Handle NULL / legacy / unknown `tip_id`: fallback to name="Unbekannt", color="#6b7280", icon="?".
   - Check how rows are instantiated into `HistoryCardWidget` and what arguments are passed.
2. Review `tests/test_prokit_e2e.py` for all Tier 1–4 tests covering History UI:
   - Identify test classes (e.g. `TestTier1HistoryBadges`, `TestTier2HistoryBoundaries`, etc.) and exact assertions.
   - Document any required attribute names, method names, or signal names.

Write your report to `/Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_1/handoff.md` and notify parent when done.
