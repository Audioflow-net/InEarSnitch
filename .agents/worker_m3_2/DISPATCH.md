## 2026-09-22T07:26:07Z
You are the M3 Remediation Worker for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_m3_2

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read the defect report from Challenger 1:
/Users/ben/Desktop/InEarSnitch/.agents/challenger_m3_1/handoff.md
Also read:
- /Users/ben/Desktop/InEarSnitch/main.py
- /Users/ben/Desktop/InEarSnitch/smoke_test.py

DEFECT TO REMEDIATE:
In `/Users/ben/Desktop/InEarSnitch/main.py` around line 3968 (inside `save_trace_to_db`):
The boolean expression currently reads:
```python
if hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden() and config.is_prokit_unlocked())):
    val = self.combo_tip.currentData()
    if val is not None:
        tip_id = int(val)
```
Because of the `or`, when `self.combo_tip.isVisible()` is True, `config.is_prokit_unlocked()` is never checked, allowing a locked app to persist `tip_id > 1` if the combobox is visible!

REQUIRED FIX:
Make `config.is_prokit_unlocked()` the mandatory top-level condition:
```python
if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden())):
    val = self.combo_tip.currentData()
    if val is not None:
        tip_id = int(val)
```

WORKFLOW & VERIFICATION:
1. Pre-flight check: Run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (must pass 19/19).
2. Git backup: Run `git add -A && git commit -m "backup: vor ProKit gate fix main.py"`
3. Edit `/Users/ben/Desktop/InEarSnitch/main.py` to apply the fix.
4. Verify using the reproduction script from `/Users/ben/Desktop/InEarSnitch/.agents/challenger_m3_1/handoff.md § 5` to confirm `saved_tip == 1`.
5. Run: `pytest -v tests/test_prokit_adversarial_ui.py`
6. Run: `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (19/19 must pass).
7. Verify `stat -f%z /Users/ben/Desktop/InEarSnitch/inearsnitch.db` remains 16379904 bytes.
8. Git commit: `git add main.py && git commit -m "fix(prokit): strictly enforce offline unlock gate in save_trace_to_db"`
9. Write handoff to `/Users/ben/Desktop/InEarSnitch/.agents/worker_m3_2/handoff.md` and notify parent.
