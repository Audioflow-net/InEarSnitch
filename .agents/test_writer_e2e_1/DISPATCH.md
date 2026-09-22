## 2026-09-22T06:17:09Z
You are the E2E Test Suite Designer for InEarSnitch ProKit Tip-Tracking.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/test_writer_e2e_1

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/TEST_INFRA.md
- /Users/ben/Desktop/InEarSnitch/smoke_test.py
- /Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md

Your mission:
Design and implement the complete, opaque-box E2E test suite in:
/Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Requirements:
1. Derive all test cases from ORIGINAL_REQUEST.md and user specifications.
2. Structure the tests across 4 Tiers:
   - Tier 1: Feature Coverage (>=5 test cases per feature for Unlock, DB schema & migration, DB queries, UI selector, History badges, Diagnostics cards)
   - Tier 2: Boundary & Corner Cases (>=5 per feature: wrong codes, whitespace, legacy NULL tip_id, <5 measurements, 5-9 measurements, mono measurements, missing BLOBs)
   - Tier 3: Cross-Feature Combinations (Pairwise coverage of feature interactions)
   - Tier 4: Real-World Application Scenarios (>=5 full scenarios: session workflows, migration backfill, statistical reproducibility, seal leak detection, unlock roundtrip)
3. Tests must be executable with `pytest -v tests/test_prokit_e2e.py` and run against isolated temporary databases and temporary directories without modifying production data.
4. When the test suite is complete, create `/Users/ben/Desktop/InEarSnitch/TEST_READY.md` following the TEST_READY template from the project guidelines.
5. Write your handoff report to `/Users/ben/Desktop/InEarSnitch/.agents/test_writer_e2e_1/handoff.md` and update progress.md.
6. When finished, send a message to parent with the summary and path to TEST_READY.md.
