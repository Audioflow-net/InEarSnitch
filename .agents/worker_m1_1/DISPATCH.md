## 2026-09-22T06:21:49Z

eisteepfirsich

You are the Worker for Milestone 1: R1 Offline Unlock System in `config.py`.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m1_1/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m1_2/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m1_3/handoff.md
- /Users/ben/Desktop/InEarSnitch/smoke_test.py

CRITICAL CONSTRAINTS:
1. Before any code change, verify git branch is main, and run:
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   If it fails → immediate git checkout -- . (No exceptions).
2. Git backup before every change:
   git add -A && git commit -m "backup: vor ProKit Unlock config.py"
3. Write ownership: You own /Users/ben/Desktop/InEarSnitch/config.py exclusively. You may also install the unit test suite at /Users/ben/Desktop/InEarSnitch/tests/test_prokit_gate.py from /Users/ben/Desktop/InEarSnitch/.agents/explorer_m1_3/proposed_test_prokit_gate.py.

YOUR TASKS:
1. In /Users/ben/Desktop/InEarSnitch/config.py, implement:
   - VALID_CODE_HASHES: the exact set of 50 SHA256 hashes listed in ORIGINAL_REQUEST.md
   - is_prokit_unlocked() -> bool
   - unlock_prokit(code: str) -> bool (normalizing code via .strip().upper(), saving hash to .prokit_unlocked)
   - revoke_prokit() -> bool (deleting .prokit_unlocked safely and idempotently)
   - Preserve get_data_dir() and get_db_path() completely unchanged!
2. Install test suite to /Users/ben/Desktop/InEarSnitch/tests/test_prokit_gate.py.
3. Run verification:
   - python3 -m unittest tests/test_prokit_gate.py (all 9 tests must pass)
   - python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py (all 19 checks must pass)
   - Test isolated CLI verification command from handoff.md
4. Commit your changes:
   git add -A && git commit -m "feat(prokit): implement offline unlock system in config.py"
5. Write your complete handoff report to:
   /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1/handoff.md
   Update /Users/ben/Desktop/InEarSnitch/.agents/worker_m1_1/progress.md.
6. When done, send a message to parent with the summary and test results.
