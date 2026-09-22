## 2026-09-22T07:49:14Z

You are M4 History Badge & Gate Challenger for Milestone 4 (R4 history_ui.py) in the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/challenger_m4_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Your mission:
Adversarially challenge and stress-test `HistoryCardWidget` tip badges and ProKit gating:
1. Tip Badge Stress Tests (use pytest or standalone PySide6 scripts with `offscreen` platform):
   - Instantiate `HistoryCardWidget` across all seed tip profiles:
     - id=1 "Unbekannt" -> text MUST be `"?"`, background `#6b7280`, color `#a1a1aa`.
     - id=2 "Kein Aufsatz" -> text `f"○ Kein Aufsatz"`, background `#94a3b8`.
     - id=3 "Standard Foam" -> text `f"● Standard Foam"`, background `#f59e0b`.
     - id=4 "ProKit V1" -> text `f"◆ ProKit V1"`, background `#3b82f6`.
     - id=5 "ProKit V2" -> text `f"★ ProKit V2"`, background `#10b981`.
   - Corner cases:
     - `tip_id = None`, `tip_id = 999` (orphaned), `tip_id = -1`.
     - `tip_name = ""`, `tip_icon = ""`, `tip_color = ""`.
     - Legacy instantiation: `HistoryCardWidget("2026-09-22 10:00:00", "KZ ZSN", "Left")`.
2. ProKit Gate & Dynamic Reactivity:
   - When locked (`is_prokit_unlocked() == False`):
     Verify `lbl_tip_badge` and `lbl_seal` are NOT visible.
   - When unlocked (`unlock_prokit(...)`):
     Call `update_prokit_visibility(True)` or `update_prokit_ui_visibility()`:
     Verify `lbl_tip_badge` and `lbl_seal` become visible immediately.
   - Re-lock (`revoke_prokit()`):
     Verify they hide immediately.
3. CRITICAL SAFETY: NEVER touch `inearsnitch.db`. Use temporary databases or memory.
4. Run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` to confirm zero regressions.

Write your report to `/Users/ben/Desktop/InEarSnitch/.agents/challenger_m4_1/handoff.md` with explicit verdict: APPROVE or REQUEST_CHANGES. Notify parent when done.
