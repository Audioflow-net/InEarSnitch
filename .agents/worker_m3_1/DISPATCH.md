## 2026-09-22T07:09:25Z
You are the M3 UI Worker for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_m3_1

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read the detailed M3 Explorer handoffs which contain exact blueprints and drop-in code snippets:
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_1/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_2/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_3/handoff.md
Also read:
- /Users/ben/Desktop/InEarSnitch/main.py
- /Users/ben/Desktop/InEarSnitch/config.py
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/smoke_test.py

LOCKED DESIGN DECISIONS:
1. Freitext is FORBIDDEN: `combo_tip` MUST NOT be editable (`combo_tip.setEditable(False)`). All tips from `TipProfiles`.
2. L and R channels ALWAYS separate.
3. tip_id = 1 for Unbekannt.
4. Depth-drift detection is impossible; do not implement.
5. Reproducibility score strictly band-limited to 20 Hz – 8 kHz.
6. Reproducibility requires >= 5 measurements.

CRITICAL CODE CONSTRAINTS:
- Exclusive write ownership: you may ONLY edit `/Users/ben/Desktop/InEarSnitch/main.py`.
- DO NOT rename, remove, or break any critical widget checked by `smoke_test.py`:
  `combo_musician`, `combo_iem`, `btn_capture`, `input_gain`, `btn_toggle_phase`, `btn_undo`, `btn_redo`, `btn_auto_scale`, `theme_selector`.
- Keep `stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db` untouched (16379904 bytes).

WORKFLOW & ACCEPTANCE CRITERIA:
1. Pre-flight check: Run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (must pass 19/19).
2. Git backup: Run `git add -A && git commit -m "backup: vor ProKit UI main.py"`
3. Implement `main.py`:
   - Add module-level alias: `InEarSnitchApp = MainWindow`
   - In `MainWindow`:
     - Assign `self.lbl_logo = logo`, `self.lbl_title = logo`, `self.lbl_sublogo = sublogo` in the header layout.
     - Install `LogoTripleClickFilter` on `self.lbl_logo` (handling press/dblclick sequences within 600ms) to trigger `self.prompt_prokit_unlock()`.
     - In bottom bar `control_panel` layout: add `self.tip_container = QWidget()` inside `right_group` immediately before `mod_capture`.
     - In `tip_container`: add `self.combo_tip = QComboBox()`, alias `self.cb_tip = self.combo_tip`, `setObjectName("cb_prokit_tip")`.
     - Strictly non-editable: `self.combo_tip.setEditable(False)`.
     - Populate with `self.db.get_all_tips(include_unknown=True)`: `display_text = f"{tip['icon_char']} {tip['name']}".strip()`, `userData = tip['id']`.
     - Default selection: select tip where `is_default == 1` (ProKit V2, id=5).
     - Visibility: `self.tip_container.setVisible(config.is_prokit_unlocked())`.
     - In `on_profile_selected` (or when IEM profile changes):
       - Query `last_tip_id = self.db.get_last_used_tip(self.current_iem_id)`.
       - If `last_tip_id` found, set `combo_tip` to that tip; else set to default tip (`is_default == 1`, ProKit V2, id=5).
     - In `save_trace_to_db`:
       - Retrieve `tip_id`: `self.combo_tip.currentData() if hasattr(self, 'combo_tip') and self.combo_tip.isVisible() else 1`. Coerce None to 1.
       - Pass `tip_id=tip_id` to `self.db.save_measurement(...)`.
     - Implement `prompt_prokit_unlock(self)`:
       - Open `QInputDialog.getText(self, "ProKit Freischaltung", "Freischaltcode eingeben:")`.
       - If user clicks OK and enters code:
         - Call `config.unlock_prokit(code)`.
         - If True: `QMessageBox.information(self, "Erfolg", "ProKit erfolgreich freigeschaltet!")`, call `self.update_prokit_ui_visibility()`.
         - If False: `QMessageBox.warning(self, "Ungültiger Code", "Der eingegebene Freischaltcode ist ungültig.")`.
     - Implement `update_prokit_ui_visibility(self)`:
       - Update `self.tip_container.setVisible(config.is_prokit_unlocked())`.
       - If unlocked: populate `self.combo_tip` and set default / last-used tip.
4. Run tests:
   `pytest -v tests/test_prokit_e2e.py -k "TestTier1UISelector or TestTier2UIBoundaries or test_profile_switching_restores_tip or test_save_measurement_flow_captures_active_tip or test_triple_click_unlock_flow"`
   Must pass all targeted tests.
5. Run smoke test:
   `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (must pass 19/19).
6. Verify `inearsnitch.db` is untouched (16379904 bytes).
7. Git commit:
   `git add main.py && git commit -m "feat(prokit): implement tip selector and triple-click unlock in main.py"`
8. Write detailed handoff report to `/Users/ben/Desktop/InEarSnitch/.agents/worker_m3_1/handoff.md` and send completion message to parent.
