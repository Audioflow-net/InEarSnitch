# BRIEFING — 2026-09-22T08:15:00+02:00

## Mission
Investigate backend implementation in `config.py` and `database.py` for InEarSnitch ProKit Tip-Tracking, check `smoke_test.py`, and design exact schema migrations, SQL, and database methods.

## 🔒 My Identity
- Archetype: explorer
- Roles: read-only investigation, backend database analysis, SQL schema design
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_survey_db_1
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: ProKit Tip-Tracking Backend Exploration

## 🔒 Key Constraints
- Read-only investigation — do NOT modify application source code (only write to our own agent directory)
- Follow Handoff Protocol (5 components: Observation, Logic Chain, Caveats, Conclusion, Verification Method)
- Keep heartbeat updated in progress.md

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T08:10:22+02:00

## Investigation State
- **Explored paths**:
  - `/Users/ben/Desktop/InEarSnitch/config.py`
  - `/Users/ben/Desktop/InEarSnitch/database.py`
  - `/Users/ben/Desktop/InEarSnitch/smoke_test.py`
  - `/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md`
  - `/Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md`
  - `/Users/ben/Desktop/InEarSnitch/.agents/rules/`
  - `/Users/ben/Desktop/InEarSnitch/main.py` (save_trace_to_db, live RTA)
  - `/Users/ben/Desktop/InEarSnitch/history_ui.py` (load_history, BLOB extraction)
  - `/Users/ben/Desktop/InEarSnitch/analysis.py` (diagnostics, band evaluation)
- **Key findings**:
  - `config.py`: `get_data_dir()` yields `~/Documents/InEarSnitch`. `.prokit_unlocked` path is `os.path.join(get_data_dir(), ".prokit_unlocked")`. `is_prokit_unlocked()`, `unlock_prokit(code)`, `revoke_prokit()` fully designed and tested against the 50 SHA256 hashes.
  - `database.py`: Open/close per operation connection pattern. Existing migrations use `try: cursor.execute("ALTER TABLE ...") except: pass` in `_init_db()`.
  - BLOB format: Raw numpy arrays serialized via `tobytes()` and deserialized via `np.frombuffer(blob, dtype=np.float64)`. Channels can be mono (Left only, Right only) or stereo. Frequency grids can have varying lengths across sample rates (e.g. 24001, 33076, 72001), requiring `np.interp` onto a common logarithmic grid (20–8000 Hz) for cross-measurement statistics.
  - `smoke_test.py`: 19/19 checks pass. Database and config changes are fully orthogonal to smoke test checks.
- **Unexplored areas**:
  - UI frontend rendering details in `main.py` and `history_ui.py` (handled by UI explorers).

## Key Decisions Made
- `TipProfiles` table designed with columns: `id`, `name`, `material`, `color_hex`, `icon_char`, `is_default`.
- Seed data uses `INSERT OR IGNORE` with explicit IDs: 1='Unbekannt', 2='Kein Aufsatz', 3='Standard Foam', 4='ProKit V1', 5='ProKit V2'.
- Migration pattern: `ALTER TABLE Measurements ADD COLUMN tip_id INTEGER REFERENCES TipProfiles(id) DEFAULT 1` in `try/except sqlite3.OperationalError` followed by `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL`.
- `save_measurement()` extended with optional `tip_id=1` (preserving backwards compatibility).
- `get_reproducibility_scores(iem_id, tip_id)` evaluates over log-spaced `np.geomspace(20, 8000, 500)` via `np.interp`, calculates std dev per frequency bin across $N \ge 5$ measurements with `ddof=1`, returns separate Left and Right dicts or `None` if < 5 measurements.
- `get_seal_history(iem_id, tip_id)` computes 40 Hz mean vs 500 Hz mean delta ($val_{40} - val_{500}$) per measurement from BLOBs, returned separately for Left and Right with `status='OK'` ($\ge -12\text{ dB}$) or `'LEAK'` ($< -12\text{ dB}$).

## Artifact Index
- `handoff.md` — Complete, structured technical report following 5-component protocol
- `progress.md` — Liveness heartbeat and progress log
- `DISPATCH.md` — Incoming task dispatch record
