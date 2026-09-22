## 2026-09-22T07:49:14Z
You are M4 Acoustic Seal Challenger for Milestone 4 (R4 history_ui.py) in the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/challenger_m4_2

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Your mission:
Adversarially challenge and stress-test acoustic seal computation and Locked Design Decision 2 (L and R ALWAYS separate) in `history_ui.py`:
1. Seal Calculation Accuracy & Thresholds:
   - Test synthetic sweeps where delta (40 Hz vs 500 Hz) crosses `-11.8 dB` threshold:
     - delta = -11.7 dB -> "OK"
     - delta = -11.8 dB -> "OK"
     - delta = -11.9 dB -> "LEAK"
   - Confirm dedicated `lbl_seal_l` and `lbl_seal_r` reflect these statuses accurately.
2. Locked Design Decision 2 (L and R ALWAYS separate):
   - Asymmetric stereo measurement: Left channel has delta = -5.0 dB ("OK"), Right channel has delta = -15.0 dB ("LEAK").
   - Verify `lbl_seal_l` shows "OK" and `lbl_seal_r` shows "LEAK".
   - Verify they are NEVER averaged (the average would be -10.0 dB, which is OK; averaging would falsely hide the right leak!).
3. Mono and Malformed BLOB Tests:
   - Mono Left (mag_r is None): `lbl_seal_l` visible, `lbl_seal_r` hidden, `lbl_seal.text()` is `"Seal L: ..."`.
   - Mono Right (mag_l is None): `lbl_seal_r` visible, `lbl_seal_l` hidden, `lbl_seal.text()` is `"Seal R: ..."`.
   - Empty frequencies or magnitudes -> no crash, seal labels gracefully hidden.
   - Truncated frequencies (e.g. 100 Hz to 10 kHz, missing 40 Hz) -> no crash, seal labels gracefully hidden.
4. CRITICAL SAFETY: NEVER touch `inearsnitch.db`. Run tests using temporary mock data.
5. Run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`.

Write your report to `/Users/ben/Desktop/InEarSnitch/.agents/challenger_m4_2/handoff.md` with explicit verdict: APPROVE or REQUEST_CHANGES. Notify parent when done.
