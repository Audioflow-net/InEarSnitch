# BRIEFING — 2026-09-22T07:39:45Z

## Mission
Analyze acoustic seal indicators (BLOB calculation, L/R separation, ProKit gating) on HistoryCardWidget for Milestone 4 (R4 history_ui.py) and formulate drop-in recommendations for the Worker.

## 🔒 My Identity
- Archetype: explorer
- Roles: investigation, analysis, synthesis
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_3
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 4 (R4 history_ui.py) - BLOB Seal & Gate Explorer

## 🔒 Key Constraints
- Read-only investigation — do NOT implement changes in source code
- LOCKED DESIGN DECISION 2: L and R channels MUST ALWAYS BE SEPARATE! Two distinct indicators on the card: `L: OK/LEAK` and `R: OK/LEAK` (e.g. `lbl_seal_l`, `lbl_seal_r` or badge). Never combine or average Left and Right!
- ProKit gating: Seal indicators only visible/rendered when `config.is_prokit_unlocked()` is True. Hidden when locked.
- Acoustic seal threshold: evaluate `val_40` (mean 35-45 Hz) vs `val_500` (mean 450-550 Hz), `delta_db = val_40 - val_500`. Threshold: `delta_db >= -11.8` or `-12.0` -> `OK`, else `LEAK`.
- Check `tests/test_prokit_e2e.py` for exact seal status assertions on history cards.

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:39:45Z

## Investigation State
- **Explored paths**:
  - `history_ui.py`: lines 50-101 (`HistoryCardWidget`), lines 452-542 (`load_history`)
  - `database.py`: lines 306-391 (`get_seal_history`)
  - `main.py`: lines 3575-3585 (live seal check), lines 4084-4108 (`update_prokit_ui_visibility`)
  - `tests/test_prokit_e2e.py`: lines 514-560 (T1-Hist), 957-1004 (T2-Hist), 1106-1127 (T3-Hist)
  - `tests/test_prokit_adversarial_db.py`: lines 476-505 (seal boundary tests)
  - `tests/test_adversarial_dsp.py`: lines 397-465 (seal threshold boundary tests)
- **Key findings**:
  - Exact threshold in `database.py` line 354 & 375 and `test_adversarial_dsp.py` is `delta_db >= -11.8`.
  - Stored BLOBs `frequencies`, `magnitude_l`, `magnitude_r` are float64 arrays already decoded in `load_history`.
  - L/R channels must never be averaged; separate indicators `lbl_seal_l` and `lbl_seal_r` with OK/LEAK badges.
  - HistoryCardWidget width is 220px-345px; a clean 2-row layout cleanly fits IEM title, side, graph, date, tip badge, and L/R seal badges without overflow.
  - Gating: all ProKit elements (`lbl_tip_badge`, `lbl_seal_l`, `lbl_seal_r`) are toggled via `config.is_prokit_unlocked()`.
- **Unexplored areas**: None for M4 BLOB Seal & Gate scope.

## Key Decisions Made
- Recommending `SEAL_THRESHOLD_DB = -11.8` for 100% mathematical consistency with `database.py`.
- Recommending 2-row card layout with explicit `lbl_seal_l` ("L: OK/LEAK") and `lbl_seal_r` ("R: OK/LEAK"), plus auxiliary `lbl_seal` attribute matching `test_prokit_e2e.py` format.
- Adding dynamic `update_prokit_visibility()` methods on both `HistoryCardWidget` and `HistoryWidget`.

## Artifact Index
- DISPATCH.md — Initial mission dispatch
- progress.md — Liveness heartbeat
- BRIEFING.md — Working memory index
- handoff.md — Complete 5-component technical analysis report
