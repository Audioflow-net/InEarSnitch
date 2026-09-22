## 2026-09-22T07:03:31Z
You are M3 Spec & UI Layout Miner for Milestone 3 (R3 main.py) in the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/main.py
- /Users/ben/Desktop/InEarSnitch/smoke_test.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Your mission:
1. Examine `main.py` bottom bar and layout:
   - Identify the bottom bar layout where `btn_capture` / RUN button is located.
   - Design the placement of the non-editable `combo_tip` (or `tip_selector`) QComboBox widget next to or near `btn_capture`.
   - Ensure `combo_tip.setEditable(False)` (Freitext is strictly forbidden).
   - How should `combo_tip` be populated with `DatabaseManager.get_all_tips(include_unknown=True)`? Format for text and `userData` storing `tip['id']`.
   - How should visibility be controlled based on `config.is_prokit_unlocked()`?
   - Default selection logic: select tip with `is_default == 1` (ProKit V2, id=5).
2. Verify that all 9 critical widget references in `smoke_test.py` are preserved completely untouched:
   `combo_musician`, `combo_iem`, `btn_capture`, `input_gain`, `btn_toggle_phase`, `btn_undo`, `btn_redo`, `btn_auto_scale`, `theme_selector`.
3. Check `tests/test_prokit_e2e.py` for all Tier 1 and Tier 2 UI selector requirements.

Write your report to `/Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1/handoff.md` and notify parent when done.
