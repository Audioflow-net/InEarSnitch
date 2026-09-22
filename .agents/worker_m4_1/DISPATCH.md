## 2026-09-22T07:41:15Z

User request:
You are the M4 Implementation Worker for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_m4_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_1/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_2/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_3/handoff.md
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You have exclusive write ownership of `/Users/ben/Desktop/InEarSnitch/history_ui.py`. Do NOT touch any other source file.

CRITICAL WORKFLOW CONSTRAINTS:
1. BEFORE ANY CODE EDIT, run pre-flight smoke test:
   `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`
   If it fails -> STOP and run `git checkout -- .`.
2. Git backup BEFORE any change:
   `git add -A && git commit -m "backup: vor ProKit history_ui.py"`
3. Implement Milestone 4 (R4 history_ui.py):
   A. `HistoryCardWidget` refactor:
      - Backward-compatible constructor:
        `def __init__(self, timestamp, iem_name, side, parent=None, tip_id=1, tip_name="Unbekannt", tip_color="#6b7280", tip_icon="?", tip_material="Standard", seal_l=None, seal_r=None, seal_text="", freq=None, mag_l=None, mag_r=None, **kwargs):`
      - Compute seal if not passed: delta = val_40 - val_500 with threshold >= -11.8 for OK, < -11.8 for LEAK.
      - Ensure Locked Design Decision 2 (L and R ALWAYS separate):
        Maintain dedicated `lbl_seal_l` and `lbl_seal_r` for Left and Right channels, and `lbl_seal` with formatted text (`Seal: L +2.1dB | R -1.4dB`, or `Seal L: -2.5dB` for mono).
      - Ensure Tip Badge:
        `lbl_tip_badge` (with aliases `tip_badge`, `lbl_badge`).
        If `tip_id == 1` or `tip_name == "Unbekannt"`: text is `"?"`, style has `background-color: #6b7280; color: #a1a1aa;`.
        If `tip_id != 1`: text is `f"{tip_icon} {tip_name}"`, style has `background-color: {tip_color}; color: white;`.
      - ProKit Gating:
        `self.lbl_tip_badge.setVisible(config.is_prokit_unlocked())`
        `self.lbl_seal.setVisible(config.is_prokit_unlocked() and bool(self.seal_text))`
        `self.lbl_seal_l.setVisible(config.is_prokit_unlocked() and self.seal_l_status is not None)`
        `self.lbl_seal_r.setVisible(config.is_prokit_unlocked() and self.seal_r_status is not None)`
      - Provide `update_prokit_visibility(self, unlocked=None)` method.
      - Preserve critical objectNames (`lbl_iem`, `lbl_date`, `lbl_side`, `cb_graph`).
   B. `HistoryWidget.load_history()` SQL update:
      - Query `Measurements` with `LEFT JOIN TipProfiles t ON m.tip_id = t.id`:
        `SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name, m.meas_name, COALESCE(m.tip_id, 1) AS tip_id, COALESCE(t.name, 'Unbekannt') AS tip_name, COALESCE(t.icon_char, '?') AS tip_icon, COALESCE(t.color_hex, '#6b7280') AS tip_color FROM Measurements m JOIN IEM_Models iem ON m.iem_id = iem.id LEFT JOIN TipProfiles t ON m.tip_id = t.id WHERE iem.musician_id = ? ORDER BY m.timestamp DESC LIMIT 100`
      - Decode numpy BLOBs, compute seal metrics, construct `data_dict` (including tip fields and seal fields), instantiate `HistoryCardWidget`.
   C. Add `HistoryWidget.update_prokit_ui_visibility(self)` to iterate over cards and call `card.update_prokit_visibility(unlocked)`.

4. VERIFICATION & DB SAFETY:
   - Run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` -> must pass 19/19 checks.
   - Run `pytest -v tests/test_prokit_e2e.py -k "History"` -> all history tests must pass.
   - Check database size: `ls -l /Users/ben/Desktop/InEarSnitch/inearsnitch.db` -> MUST BE EXACTLY 16379904 bytes.
   - Git commit: `git add -A && git commit -m "feat(prokit): implement tip badges and acoustic seal in history_ui.py"`
