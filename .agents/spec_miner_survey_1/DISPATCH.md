## 2026-09-22T06:10:22Z
You are the Requirements Spec Miner for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md
- /Users/ben/Desktop/InEarSnitch/.agents/rules/prokit_system.md
- /Users/ben/Desktop/InEarSnitch/.agents/rules/live_features_guard.md
- /Users/ben/Desktop/InEarSnitch/smoke_test.py

Your mission:
Survey and extract the exhaustive specification for ProKit Tip-Tracking:
1. All locked design decisions (freetext forbidden, L/R separate, legacy tip_id=1 Unbekannt, depth-drift detection impossible, 20Hz-8kHz band-limited reproducibility score, >=5 measurements required).
2. R1 config.py: All functions, exact 50 SHA256 hashes, file path `.prokit_unlocked` in `get_data_dir()`.
3. R2 database.py: TipProfiles schema, migration strategy (try/except ALTER TABLE), seed order (Unbekannt id=1 first, etc.), legacy backfill UPDATE query, and all new/modified methods.
4. R3 main.py: Tip ComboBox in bottom bar, conditional visibility via `is_prokit_unlocked()`, auto-suggest last-used tip for current IEM, passing tip_id to save_measurement(), triple-click logo unlock dialog.
5. R4 history_ui.py: Tip badge with icon_char and color_hex, LEFT JOIN query, "?" for Unbekannt, L/R seal status from stored BLOBs if unlocked.
6. R5 analysis_ui.py: Diagnostics tip card, 8kHz target peak detection (6-10kHz), reproducibility score (std dev 20Hz-8kHz, L/R separate, >=5 threshold, preliminary warning 5-9), seal history trend (40Hz vs 500Hz delta).
7. Acceptance criteria checklist and anti-regression constraints.

Write your complete, structured report to:
/Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1/handoff.md
Update /Users/ben/Desktop/InEarSnitch/.agents/spec_miner_survey_1/progress.md with your progress.
When finished, send a message to parent with the summary and path to your handoff.md.
