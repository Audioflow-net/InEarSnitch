## 2026-09-22T06:10:22Z
You are the UI & Analysis Explorer for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/main.py
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/analysis_ui.py
- /Users/ben/Desktop/InEarSnitch/theme.py
- /Users/ben/Desktop/InEarSnitch/smoke_test.py
- /Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md

Your mission:
Investigate the UI structure and integration points for ProKit Tip-Tracking:
1. `main.py`:
   - Locate the bottom bar layout near `btn_capture` / RUN button. How are widgets laid out?
   - Identify the App Logo / Title text widget in the header. How can a triple-click event filter be installed cleanly?
   - How does profile switching work? Where is the current IEM id maintained, and where should the last-used tip suggestion be triggered?
   - Where is `save_trace_to_db()` or the measurement saving flow located, and how does it call `database.save_measurement()`?
   - Identify critical widget references from `smoke_test.py` that must NEVER be broken or renamed.
2. `history_ui.py`:
   - Inspect `HistoryWidget` and `HistoryCardWidget`.
   - How is history loaded (`load_history()`)? How does it populate cards?
   - Where and how can a colored tip badge (using `icon_char` and `color_hex`) be rendered on each card?
   - How is seal status (40Hz vs 500Hz) calculated or displayed if ProKit is unlocked?
3. `analysis_ui.py`:
   - Inspect `AnalysisWidget` and `render_diagnostics()`.
   - Where are diagnostics cards created and laid out?
   - How does `render_diagnostics()` get measurement data or access `database`?
   - How should the Tip Analysis card be rendered when ProKit is unlocked?
   - How to find the 8kHz target peak in the 6–10 kHz range from stored BLOBs?
   - How to format reproducibility score and seal trend with preliminary warnings (<10) or "Not enough data" (<5)?

Write your complete, structured technical report to:
/Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1/handoff.md
Update /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_ui_1/progress.md with your progress.
When finished, send a message to parent with the summary and path to your handoff.md.
