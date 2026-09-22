## 2026-09-22T07:56:52Z

You are Worker Catalog for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_catalog

MANDATORY: Read the authoritative user request and the PRIORITY USER DIRECTIVE at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/database.py
- /Users/ben/Desktop/InEarSnitch/main.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_adversarial_db.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

CRITICAL WORKFLOW CONSTRAINTS:
1. BEFORE ANY CODE EDIT, run pre-flight smoke test:
   `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`
   If it fails -> STOP and run `git checkout -- .`.
2. Git backup BEFORE any change:
   `git add -A && git commit -m "backup: vor Real Tip Catalog Update"`

TASK DESCRIPTION:
Incorporate the PRIORITY USER DIRECTIVE into the codebase:
The user has issued a direct correction regarding TipProfiles seed data:
Seed data in TipProfiles must use the REAL tip catalog from `/Users/ben/.gemini/antigravity/brain/dc2b2fbc-d180-476f-aea9-bae3683b5971/visual_catalog.html`, replacing generic placeholders ("ProKit V1", "ProKit V2", "Standard Foam").

Replace the seed data in `database.py` with these REAL tip models:
```python
default_tips = [
    # id=1 MUST be "Unbekannt" (legacy fallback) — DO NOT CHANGE
    ("Unbekannt", "Legacy-Messung ohne Tip-Information", "", "#444444", "?", 0),
    ("Kein Aufsatz", "Direkt ohne Tip gemessen", "", "#555555", "○", 0),
    ("V26 Straight", "Bester Allrounder — gerade 90°-Kante", "Silicone", "#22c55e", "▮", 1),
    ("V27 Rounded", "Komfort-Update — 2mm Abrundung an der Spitze", "Silicone", "#3b82f6", "▮", 0),
    ("V29-C Cone", "Konisch zulaufend — extremer Seal durch tiefes Einpressen", "Silicone", "#f97316", "◆", 0),
    ("V30-C Pro", "9mm Torus-Lippe, 4mm Loch — Stabilitäts-Upgrade", "Silicone", "#3b82f6", "◉", 0),
    ("V31-XL Panzer", "10mm Lippe, 6mm Loch — für fette Custom In-Ears", "Silicone", "#f97316", "◉", 0),
]
```

Notes:
- V28 Universal is EXCLUDED (verworfen/deprecated — "Choke-Tube Akustik" problem)
- V26 Straight is `is_default=1` (marked as "Bester Allrounder" in the catalog)
- All tips are Silicone material (these are silicone adapters with matching tamper/stamps)
- Each tip has a matching "Tamper" (stamp for the silicone mold) — not relevant for the DB but good context

1. In `database.py`:
   - In `_init_db`:
     - Ensure `TipProfiles` table has `description TEXT DEFAULT ''` (add via PRAGMA table_info check / ALTER TABLE if missing).
     - Populate or update `TipProfiles` with the 7 real tips above deterministically with IDs 1 to 7:
       `id=1`: Unbekannt
       `id=2`: Kein Aufsatz
       `id=3`: V26 Straight (is_default=1)
       `id=4`: V27 Rounded
       `id=5`: V29-C Cone
       `id=6`: V30-C Pro
       `id=7`: V31-XL Panzer
       Use an upsert (`INSERT ... ON CONFLICT(id) DO UPDATE SET ...`) or clean seeding so existing databases are seamlessly updated.
     - In `get_all_tips()`: include `description` field in the returned dictionary.
2. In `main.py`:
   - In `update_tip_selector()` and `suggest_tip_for_current_iem()`:
     - When selecting default tip, dynamically find the tip with `is_default == 1` (or fallback to id=3 "V26 Straight"), rather than hardcoding id=5.
3. In `tests/test_prokit_e2e.py` and other test files:
   - Update seed catalog tests to assert the real catalog:
     - `test_tipprofiles_seed_data_deterministic_order`:
       assert len(rows) >= 7
       rows[0] is Unbekannt (id=1, is_default=0)
       rows[1] is Kein Aufsatz (id=2, is_default=0)
       rows[2] is V26 Straight (id=3, is_default=1)
       rows[3] is V27 Rounded (id=4, is_default=0)
       rows[4] is V29-C Cone (id=5, is_default=0)
       rows[5] is V30-C Pro (id=6, is_default=0)
       rows[6] is V31-XL Panzer (id=7, is_default=0)
     - `test_tip_selector_populated_from_database`:
       assert cb.count() == 6 (excluding unknown)
       assert cb.itemData(0) == 2  # Kein Aufsatz
       assert cb.itemData(1) == 3  # V26 Straight
     - `test_selector_save_and_history_badge_roundtrip`:
       use selected_tip = 3 (V26 Straight) or 5 (V29-C Cone), with corresponding name, icon, and color.
     - `test_history_mixed_legacy_and_prokit_badges`:
       update assertions for the tested tip IDs (e.g. id=4 V27 Rounded with "▮", id=5 V29-C Cone with "◆", etc.).
     - `test_scenario_legacy_migration_and_compatibility`:
       update row 20 assertion to match tip 4 ("V27 Rounded").
   - In `tests/test_prokit_adversarial_db.py`:
     - Update default tip assertion from (5, "ProKit V2") to (3, "V26 Straight").
     - Update tips[2], tips[3], etc., names to match V26 Straight, V27 Rounded, etc.
   - In `tests/test_history_badge_gate_adversarial.py`:
     - If any tests assert "ProKit V1" on seed ids, update them to match the new catalog or ensure they test custom injected tips.

4. CRITICAL VERIFICATION & DB SAFETY:
   - `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` -> 19/19 CHECKS PASSED.
   - `pytest -v tests/test_prokit_e2e.py`
   - `pytest -v tests/test_prokit_adversarial_db.py`
   - `pytest -v tests/test_prokit_adversarial_ui.py`
   - `pytest -v tests/test_adversarial_dsp.py`
   - Check database size: `ls -l /Users/ben/Desktop/InEarSnitch/inearsnitch.db` -> MUST BE EXACTLY 16379904 bytes!
   - Git commit: `git add -A && git commit -m "feat(prokit): update TipProfiles to real physical tip catalog"`

Write your handoff report to `/Users/ben/Desktop/InEarSnitch/.agents/worker_catalog/handoff.md` and notify parent when done.
