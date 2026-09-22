# BRIEFING — 2026-09-22T07:25:00Z

## Mission
Adversarially challenge and stress-test the UI selector, dynamic visibility, and data flow in main.py for ProKit Tip-Tracking.

## 🔒 My Identity
- Archetype: empirical_challenger
- Roles: critic, specialist
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/challenger_m3_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: M3
- Instance: 1 of 1

## 🔒 Key Constraints
- Review-only — do NOT modify implementation code
- All tests MUST use temporary databases (tmp_path or tempfile). NEVER touch inearsnitch.db!
- .agents/ holds only agent metadata — NEVER place source code, tests, or data files here.
- Must execute tests empirically, not just speculate.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:18:48Z

## Review Scope
- **Files to review**: main.py, tests/test_prokit_e2e.py
- **Interface contracts**: /Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md, /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- **Review criteria**: combo_tip non-editable, dynamic visibility of tip_container when ProKit locked/unlocked, persistence of tip_id=1 when locked, persistence of selected tip_id when unlocked, IEM profile switching & tip restoration / fallback to id=5 on legacy measurements.

## Attack Surface
- **Hypotheses tested**:
  1. combo_tip can be edited via keyboard or freetext injection -> DISPROVEN (rigidly non-editable, lineEdit is None).
  2. tip_container visibility does not track unlock lifecycle -> DISPROVEN (properly synchronized across 50 rapid flips).
  3. 5 IEM profiles fail to restore specific tips or fallback to tip 5 -> DISPROVEN (fully restored in forward & reverse).
  4. save_trace_to_db allows saving ProKit tip while locked if widget is visible -> CONFIRMED VULNERABILITY (main.py:3968 boolean condition flaw).
- **Vulnerabilities found**:
  - `main.py:3968`: Operator precedence flaw in `save_trace_to_db` where `self.combo_tip.isVisible()` on left side of `or` is not guarded by `config.is_prokit_unlocked()`. Empirically reproduced and confirmed that `tip_id=4` was written to DB while locked.
- **Untested angles**:
  - Wayland-specific display server events (tested on macOS Cocoa/offscreen).

## Loaded Skills
None

## Key Decisions Made
- Authored 21 empirical adversarial tests in `tests/test_prokit_adversarial_ui.py`.
- Formulated explicit verdict: REQUEST_CHANGES targeting `main.py:3968`.

## Artifact Index
- DISPATCH.md — incoming dispatch instructions
- BRIEFING.md — situational awareness
- progress.md — liveness heartbeat
- handoff.md — final challenge report (REQUEST_CHANGES)
- tests/test_prokit_adversarial_ui.py — 21 automated adversarial stress tests
