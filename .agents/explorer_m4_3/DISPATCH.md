## 2026-09-22T07:34:58Z
You are M4 BLOB Seal & Gate Explorer for Milestone 4 (R4 history_ui.py) in the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_3

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/config.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Your mission:
1. Examine acoustic seal indicators on `HistoryCardWidget`:
   - How can seal status be calculated from stored BLOBs (`frequencies`, `magnitude_l`, `magnitude_r`) on each measurement row?
   - Evaluate `val_40` (mean 35–45 Hz) vs `val_500` (mean 450–550 Hz), `delta_db = val_40 - val_500`.
   - Threshold: `delta_db >= -11.8` or `-12.0` -> `OK`, else `LEAK`.
   - LOCKED DESIGN DECISION 2: L and R channels MUST ALWAYS BE SEPARATE!
     Two distinct indicators on the card: `L: OK/LEAK` and `R: OK/LEAK` (e.g. `lbl_seal_l`, `lbl_seal_r` or badge).
     Never combine or average Left and Right!
   - Gating: Only visible/rendered when `config.is_prokit_unlocked()` is True. Hidden when locked.
2. Review `tests/test_prokit_e2e.py` for exact seal status assertions on history cards.
3. Formulate complete drop-in code recommendations for the Worker.

Write your report to `/Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_3/handoff.md` and notify parent when done.
