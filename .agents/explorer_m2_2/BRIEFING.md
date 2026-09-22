# BRIEFING — 2026-09-22T08:38:45+02:00

## Mission
Investigate and design query and DSP analytical methods for `database.py` (M2 R2), including `get_all_tips`, `get_last_used_tip`, `get_reproducibility_scores`, and `get_seal_history`.

## 🔒 My Identity
- Archetype: Teamwork explorer
- Roles: Investigation, DSP analysis, Query design, Synthesis
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m2_2
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 2 (R2 database.py query & DSP)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement directly in source code
- Strictly separate Left and Right channels (never merge)
- Band-limited strictly to 20 Hz – 8000 Hz using logarithmic interpolation (e.g. `np.geomspace(20, 8000, 500)`)
- Reproducibility requires >= 5 measurements per channel (returns None if < 5)
- Reproducibility sets `is_preliminary = True` if 5 <= count < 10
- Seal history delta threshold: delta >= -12.0 dB is OK, delta < -12.0 dB is LEAK
- `get_last_used_tip` strictly excludes id=1 ("Unbekannt")
- Deliver findings in `handoff.md` and notify parent via `send_message`

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T08:38:45+02:00

## Investigation State
- **Explored paths**:
  - `database.py`: Existing schema, BLOB serialization (`array.tobytes()`), deserialization (`np.frombuffer(..., dtype=np.float64)`).
  - `ORIGINAL_REQUEST.md`: LOCKED design decisions (freetext forbidden, L/R separate, 20-8000 Hz band limit, N>=5 threshold, 5-9 preliminary warning).
  - `tests/test_prokit_e2e.py`: Tier 1 DB queries, Tier 2 DSP boundaries, and Tier 4 real-world scenarios.
  - `main.py:3466-3476`: Real-time RTA seal calculation logic (40 Hz vs 500 Hz, delta >= -12.0 dB is OK).
- **Key findings**:
  1. `get_all_tips(include_unknown=True)`: Clean SQLite query with `sqlite3.Row` returning dicts with 6 fields.
  2. `get_last_used_tip(iem_id)`: Excludes `id=1` and `NULL`, sorted by `timestamp DESC, id DESC LIMIT 1`. Returns `int` or `None`.
  3. `get_reproducibility_scores(iem_id, tip_id)`: Requires `f <= 8000.0` filtering before `np.interp` on `np.geomspace(20, 8000, 500)` to prevent HF coupler resonance variance leaking into boundary bin at 8000 Hz. Sample std with `ddof=1`.
  4. `get_seal_history(iem_id, tip_id)`: Evaluates 35-45 Hz vs 450-550 Hz means from stored BLOBs. L/R separate. Threshold delta >= -12.0 dB.
  5. Test discrepancy in `test_prokit_e2e.py:392`: `create_synthetic_sweep(leak_db=15.0)` without `bass_boost_db=0.0` leaves net delta at -11.82 dB (+0.18 dB above -12.0 dB) due to default 3 dB boost and downward tilt.
- **Unexplored areas**: None for M2 Query & DSP scope.

## Key Decisions Made
- All method designs verified against synthetic data generators and isolated database fixtures.
- Complete drop-in code prepared for M2 Worker.

## Artifact Index
- DISPATCH.md — Parent dispatch instruction
- BRIEFING.md — Persistent memory
- progress.md — Liveness tracker
- handoff.md — Comprehensive handoff report for Worker & Parent
