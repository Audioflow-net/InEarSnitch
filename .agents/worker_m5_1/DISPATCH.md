## 2026-09-22T08:17:03Z
You are the M5 Implementation Worker for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_m5_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/analysis_ui.py
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m5_1/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m5_2/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m5_3/handoff.md
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You have exclusive write ownership of `/Users/ben/Desktop/InEarSnitch/analysis_ui.py`. Do NOT touch any other source file.

CRITICAL WORKFLOW CONSTRAINTS:
1. BEFORE ANY CODE EDIT, run pre-flight smoke test:
   `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`
   If it fails -> STOP and run `git checkout -- .`.
2. Git backup BEFORE any change:
   `git add -A && git commit -m "backup: vor ProKit analysis_ui.py"`

TASK SPECIFICATION:
Implement Milestone 5 (R5 analysis_ui.py — Tip Analysis Card in Diagnostics):
1. Create `TipAnalysisCardWidget(QFrame)` in `analysis_ui.py`:
   - `TARGET_HELMHOLTZ_HZ = 8000.0`
   - Peak detection method `detect_helmholtz_peak(freqs, mag)` in 6,000 Hz – 10,000 Hz window for Left and Right channels separately. Fall back to historical median peak from `db.get_tip_target_peak(iem_id, tip_id)` when live sweep data is not available.
   - Band-limited reproducibility score (20 Hz – 8,000 Hz):
     - Separate L and R scores from `db.get_reproducibility_scores(iem_id, tip_id)`.
     - Strict threshold: requires >= 5 measurements. If < 5 or scores is None, display empty state:
       `f"Not enough data (min. 5 measurements required, currently N={count})"`
     - If 5–9 measurements: show `badge_repro_status` with `⚠ Preliminary (N={count})` (yellow/amber styling).
     - If >= 10 measurements: show `✓ Stable (N={count})` (green styling).
   - Acoustic seal history trend:
     - Summaries and micro-chips from `db.get_seal_history(iem_id, tip_id)`.
   - Header with `[PROKIT]` pill badge, title `"Ear Tip Analysis & Acoustic Coupling"`, and `cb_tip_selector` (`QComboBox`) populated from `db.get_all_tips(include_unknown=True)`.
   - Initial visibility: `self.setVisible(config.is_prokit_unlocked())`.
   - Accepts optional `db`, `iem_id`, `tip_id`, `freqs`, `mag_l`, `mag_r` for isolated standalone testing.
   - ObjectNames: `tip_analysis_card`, `cb_tip_selector`, `sec_helmholtz`, `lbl_peak_l`, `lbl_peak_r`, `sec_reproducibility`, `badge_repro_preliminary`, `lbl_repro_warning`, `lbl_score_l`, `lbl_score_r`, `sec_seal_history`.

2. Integrate into `AnalysisWidget.render_diagnostics()`:
   - Update guard at line 642: allow rendering if `config.is_prokit_unlocked()` is True, even if `_last_report` is empty, so tip statistics display for the active profile.
   - When `config.is_prokit_unlocked() and (active_cat is None or active_cat == 'FR')`:
     Instantiate `TipAnalysisCardWidget` and add to the top of `self.report_layout`.
     Connect `tip_changed` to sync with `main_window.combo_tip` if available.
   - Add method `update_prokit_visibility(self)` on `AnalysisWidget` that calls `render_diagnostics()`.

3. VERIFICATION & DB SAFETY:
   - `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` -> 19/19 CHECKS PASSED.
   - `pytest -v tests/test_prokit_e2e.py -k "Diagnostics"`.
   - `pytest -v tests/test_prokit_e2e.py` (all 87 tests).
   - Check database size: `ls -l /Users/ben/Desktop/InEarSnitch/inearsnitch.db` -> MUST BE EXACTLY 16379904 bytes!
   - Git commit: `git add -A && git commit -m "feat(prokit): implement tip analysis diagnostics card in analysis_ui.py"`.

Write your handoff report to `/Users/ben/Desktop/InEarSnitch/.agents/worker_m5_1/handoff.md` and notify parent when done.
