## 2026-09-22T06:10:22Z
You are the Core & DB Explorer for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_db_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/config.py
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/smoke_test.py

Your mission:
Investigate existing backend implementation in `config.py` and `database.py`:
1. Check `config.py`: current contents, how `get_data_dir()` works, and where `.prokit_unlocked` will be stored.
2. Check `database.py`:
   - Connection lifecycle, existing tables (`Measurements`, `Profiles`, etc.), and existing migration patterns.
   - How `save_measurement()` currently works (arguments, query, defaults).
   - How BLOBs are stored (format: numpy bytes, pickle, etc.) and how frequencies and magnitudes are extracted.
   - Design the exact SQL for `TipProfiles`, the ALTER TABLE migration, the seed data insertion, the UPDATE legacy backfill.
   - Design the new methods: `get_all_tips()`, `get_last_used_tip(iem_id)`, `get_reproducibility_scores(iem_id, tip_id)`, `get_seal_history(iem_id, tip_id)`.
3. Check `smoke_test.py` to ensure planned changes won't conflict with any existing checks.

Write your complete, structured technical report to:
/Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_db_1/handoff.md
Update /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_db_1/progress.md with your progress.
When finished, send a message to parent with the summary and path to your handoff.md.
