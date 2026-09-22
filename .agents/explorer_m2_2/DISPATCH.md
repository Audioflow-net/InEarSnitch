## 2026-09-22T06:32:44Z

You are the M2 Query & DSP Explorer for Milestone 2 (R2 database.py).
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m2_2

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_db_1/handoff.md

Your mission:
Investigate and design the query and DSP analytical methods for `database.py`:
1. `get_all_tips(include_unknown=True) -> list[dict]`.
2. `get_last_used_tip(iem_id: int) -> int | None` (strictly excluding id=1 "Unbekannt").
3. `get_reproducibility_scores(iem_id: int, tip_id: int) -> dict | None`:
   - Band-limited strictly to 20 Hz – 8000 Hz using logarithmic interpolation (e.g. `np.geomspace(20, 8000, 500)`).
   - Left and Right channels computed strictly separately (never merged).
   - Requires >= 5 measurements per channel (returns None if < 5).
   - Sets `is_preliminary = True` if 5 <= count < 10.
4. `get_seal_history(iem_id: int, tip_id: int) -> dict`:
   - Extracts 40 Hz vs 500 Hz means from stored BLOBs.
   - Left and Right channels computed strictly separately.
   - Categorizes status: delta >= -12.0 dB is OK, delta < -12.0 dB is LEAK.
5. Formulate exact Python code for the Worker.

Write your findings to /Users/ben/Desktop/InEarSnitch/.agents/explorer_m2_2/handoff.md and notify parent when done.
