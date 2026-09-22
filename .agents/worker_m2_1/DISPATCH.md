## 2026-09-22T06:53:01Z
You are the M2 Database Worker for the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/worker_m2_1

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read the detailed M2 Explorer handoffs which contain exact blueprints, SQL queries, and mathematical formulas:
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m2_1/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m2_2/handoff.md
- /Users/ben/Desktop/InEarSnitch/.agents/explorer_m2_3/handoff.md
Also read:
- /Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md
- /Users/ben/Desktop/InEarSnitch/.agents/rules/prokit_system.md
- /Users/ben/Desktop/InEarSnitch/database.py

LOCKED DESIGN DECISIONS:
1. Freitext is FORBIDDEN: all tip profiles live in `TipProfiles`.
2. L and R channels ALWAYS separate (never averaged/combined).
3. Legacy measurements (`tip_id = NULL`) automatically backfilled to "Unbekannt" (`id=1`).
4. Depth-drift detection during sweep is physically impossible; do not implement.
5. Reproducibility score strictly band-limited to 20 Hz – 8 kHz (`np.interp` on 20–8000 Hz, with pre-filtering `f <= 8000.0`).
6. Reproducibility requires >= 5 measurements (None if < 5); 5–9 shows is_preliminary=True, >=10 is_preliminary=False.

DATABASE SAFETY CRITICAL:
- /Users/ben/Desktop/InEarSnitch/inearsnitch.db is the 16.38 MB production/dev database.
- DO NOT MODIFY OR CORRUPT inearsnitch.db.
- When writing any scratch scripts or tests, NEVER call DatabaseManager() without arguments! ALWAYS provide an explicit temporary database path (`tmp_path` or `tempfile.NamedTemporaryFile`).

WORKFLOW & ACCEPTANCE CRITERIA:
1. Pre-flight check: Run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (must pass 19/19).
2. Git backup: Run `git add -A && git commit -m "backup: vor ProKit DB database.py"`
3. Implement `database.py` (exclusive write ownership):
   - Table `TipProfiles` (id, name, material, color_hex, icon_char, is_default)
   - Migration in `_init_db()`: add columns (`gain_db`, `phase_l`, `phase_r`, `notes`, `photo_path`, `tip_id INTEGER DEFAULT 1 REFERENCES TipProfiles(id)`) with `try/except sqlite3.OperationalError: pass`.
   - Legacy backfill: `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL`.
   - Seed data with `INSERT OR IGNORE INTO TipProfiles (id, name, material, color_hex, icon_char, is_default)`:
     - 1: ("Unbekannt", "Standard", "#6b7280", "?", 0)
     - 2: ("Kein Aufsatz", "None", "#94a3b8", "○", 0)
     - 3: ("Standard Foam", "Foam", "#f59e0b", "●", 0)
     - 4: ("ProKit V1", "Silicone", "#3b82f6", "◆", 0)
     - 5: ("ProKit V2", "Silicone", "#10b981", "★", 1)
   - `save_measurement()`: Add parameter `tip_id=1`. Coerce `tip_id=None` to `1`.
   - `get_all_tips(include_unknown=True)`: Return list of dicts with keys `id`, `name`, `material`, `color_hex`, `icon_char`, `is_default`. If include_unknown is False, filter `WHERE id != 1`.
   - `get_last_used_tip(iem_id)`: Return int tip_id or None. Query `WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1 ORDER BY timestamp DESC, id DESC LIMIT 1`.
   - `get_reproducibility_scores(iem_id, tip_id)`:
     - Band-limited strictly to 20 Hz - 8000 Hz.
     - Common grid `np.linspace(20.0, 8000.0, 800)`.
     - Filter `f <= 8000.0` before interpolating.
     - Process Left and Right separately.
     - Skip empty/corrupt curves (`len < 10`).
     - Require >= 5 measurements per channel (else channel score is None; if both None return None).
     - `std_per_bin = np.std(..., axis=0, ddof=0)`. `mean_std = float(round(np.mean(std_per_bin), 2))`.
     - Channel dict: `{"score": mean_std, "std_dev": mean_std, "count": len(interp), "is_preliminary": bool(len(interp) < 10)}`.
     - Return `{"left": left_res, "right": right_res}`.
   - `get_seal_history(iem_id, tip_id)`:
     - Query `id, timestamp, frequencies, magnitude_l, magnitude_r FROM Measurements WHERE iem_id = ? AND tip_id = ? ORDER BY timestamp ASC, id ASC`.
     - Evaluate `val_40` (mean 35-45 Hz) and `val_500` (mean 450-550 Hz).
     - `delta_db = float(round(val_40 - val_500, 2))`.
     - `seal_ok = bool(delta_db >= -12.0)`. `status = "OK" if seal_ok else "LEAK"`.
     - Return `{"left": [...], "right": [...]}`.
4. Verify tests:
   Run: `pytest -v tests/test_prokit_e2e.py -k "TestTier1DBSchema or TestTier1DBQueries or TestTier2DBBoundaries or TestTier2DSPBoundaries or test_unlock_and_db_catalog_interaction or test_reproducibility_isolated_per_tip or test_multi_iem_tip_persistence_and_suggestion or test_scenario_legacy_migration_and_compatibility or test_scenario_statistical_reproducibility or test_scenario_seal_leak_detection_and_degradation"`
   Must pass all 24 target tests.
5. Verify smoke test:
   Run: `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` (must pass 19/19).
6. Verify inearsnitch.db size is unchanged (16379904 bytes).
7. Git commit: `git add database.py && git commit -m "feat(prokit): implement TipProfiles schema, migration, and query methods in database.py"`
8. Write detailed handoff to `/Users/ben/Desktop/InEarSnitch/.agents/worker_m2_1/handoff.md` and send completion message to parent.
