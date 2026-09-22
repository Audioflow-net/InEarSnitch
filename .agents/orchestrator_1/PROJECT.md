# Project: InEarSnitch ProKit Tip-Tracking

## Architecture
- Module/package boundaries, data flow, shared interfaces:
  - Offline SHA256 gate in `config.py` protects all ProKit UI and analytical features without requiring internet.
  - SQLite ORM in `database.py` manages `TipProfiles` table, schema migration, legacy backfill (`tip_id = 1`), and analytical metrics from numpy BLOBs.
  - PySide6 UI in `main.py` provides bottom-bar Tip ComboBox, dynamic visibility, and triple-click logo unlock dialog.
  - PySide6 UI in `history_ui.py` renders colored tip badges and seal status on measurement history cards.
  - PySide6 UI in `analysis_ui.py` renders tip resonance peak, band-limited reproducibility score, and seal history trend.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Offline Unlock System | `config.py` functions `is_prokit_unlocked`, `unlock_prokit`, `revoke_prokit` with 50 SHA256 hashes and `.prokit_unlocked` token | M1 | Survey / R1 |
| 2 | TipProfiles Schema & Migration | `database.py` table `TipProfiles` (id, name, material, color_hex, icon_char, is_default) & `ALTER TABLE Measurements ADD COLUMN tip_id` | M2 | Survey / R2 |
| 3 | Seed TipProfiles Catalog | `database.py` deterministic seed order with id=1 "Unbekannt", id=2 "Kein Aufsatz", id=3 "Standard Foam", id=4 "ProKit V1", id=5 "ProKit V2" | M2 | Survey / R2 |
| 4 | Legacy Measurements Backfill | `database.py` `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL` | M2 | Survey / R2 |
| 5 | Database Tip Catalog Query API | `database.py` `get_all_tips(include_unknown=True)` | M2 | Survey / R2 |
| 6 | Database Last-Used Tip Query | `database.py` `get_last_used_tip(iem_id)` excluding id=1 | M2 | Survey / R2 |
| 7 | Extended save_measurement API | `database.py` `save_measurement()` with `tip_id=1` parameter | M2 | Survey / R2 |
| 8 | Band-Limited Reproducibility Query | `database.py` `get_reproducibility_scores(iem_id, tip_id)` (20Hz-8kHz, L/R separate, >=5 threshold, 5-9 preliminary warning) | M2 | Survey / R2 |
| 9 | Seal History Trend Query | `database.py` `get_seal_history(iem_id, tip_id)` (40Hz vs 500Hz, L/R separate) | M2 | Survey / R2 |
| 10 | Bottom-Bar Tip Selector ComboBox | `main.py` non-editable QComboBox in bottom bar near RUN button populated from TipProfiles | M3 | Survey / R3 |
| 11 | Dynamic ProKit Gate Visibility | `main.py` tip selector visibility toggled via `is_prokit_unlocked()` | M3 | Survey / R3 |
| 12 | Auto-Suggest Last-Used Tip | `main.py` `on_profile_selected()` auto-suggests last-used tip (excluding id=1) when switching IEM | M3 | Survey / R3 |
| 13 | Save Measurement with Active Tip | `main.py` `save_trace_to_db()` forwards selected `tip_id` to `save_measurement()` | M3 | Survey / R3 |
| 14 | Triple-Click Logo Unlock Dialog | `main.py` triple-click event filter on logo label opens unlock dialog with code entry | M3 | Survey / R3 |
| 15 | History Card Tip Badge | `history_ui.py` colored badge with `icon_char` and `color_hex` on HistoryCardWidget (grey ? for Unbekannt) | M4 | Survey / R4 |
| 16 | History Query LEFT JOIN | `history_ui.py` `load_history()` queries Measurements LEFT JOIN TipProfiles | M4 | Survey / R4 |
| 17 | History Card Seal Status | `history_ui.py` evaluates stored BLOBs (40Hz vs 500Hz) and displays separate L and R seal indicators if unlocked | M4 | Survey / R4 |
| 18 | Tip Analysis Card in Diagnostics | `analysis_ui.py` diagnostics card rendered in `render_diagnostics()` when unlocked | M5 | Survey / R5 |
| 19 | 8kHz Helmholtz Target Peak Detection | `analysis_ui.py` detects resonance peak in 6-10kHz from BLOBs for L and R | M5 | Survey / R5 |
| 20 | Reproducibility Score Card Display | `analysis_ui.py` displays band-limited score with L/R separate, >=5 threshold, 5-9 warning | M5 | Survey / R5 |
| 21 | Seal History Trend Display | `analysis_ui.py` displays 40Hz vs 500Hz trend over time with L/R separate | M5 | Survey / R5 |
| 22 | Comprehensive E2E Test Suite | 100% E2E test suite covering Tiers 1-4 with >=11*N test cases | Final | E2E Track |
| 23 | Adversarial Coverage Hardening | Tier 5 adversarial stress testing and edge-case verification | Final | E2E Track |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Offline Unlock System | config.py: is_prokit_unlocked, unlock_prokit, revoke_prokit, VALID_CODE_HASHES | none | DONE |
| M2 | Database Schema & API | database.py: TipProfiles, migration, seed, legacy backfill, get_all_tips, get_last_used_tip, save_measurement, get_reproducibility_scores, get_seal_history | none | DONE |
| M3 | Tip Selector & Unlock UI | main.py: Bottom bar QComboBox, visibility gate, profile switch auto-suggest, save_trace_to_db tip_id passing, triple-click logo unlock dialog | M1, M2 | DONE |
| M4 | History UI Tip Badges | history_ui.py: LEFT JOIN TipProfiles in load_history, HistoryCardWidget tip badge, BLOB seal status | M1, M2 | DONE |
| M5 | Diagnostics Tip Analysis | analysis_ui.py: render_diagnostics Tip Analysis card, 8kHz target peak, reproducibility score display, seal trend display | M1, M2 | DONE |
| Final | E2E Pass & Coverage Hardening | Phase 1: 100% pass of Tiers 1-4 E2E test suite. Phase 2: Tier 5 adversarial hardening | M1, M2, M3, M4, M5, E2E-Track | IN_PROGRESS |

## Interface Contracts
### config.py ↔ UI & App
- `is_prokit_unlocked() -> bool`: Returns True if `.prokit_unlocked` exists in `get_data_dir()`.
- `unlock_prokit(code: str) -> bool`: Checks SHA256 of normalized code against `VALID_CODE_HASHES`. Writes hash to `.prokit_unlocked` on success and returns True. Returns False otherwise.
- `revoke_prokit() -> bool`: Removes `.prokit_unlocked` if present. Returns True.

### database.py ↔ main.py / history_ui.py / analysis_ui.py
- `TipProfiles`: Columns `(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, material TEXT, color_hex TEXT, icon_char TEXT, is_default INTEGER DEFAULT 0)`.
- `Measurements.tip_id`: Foreign key referencing `TipProfiles(id)`, defaults to 1.
- `get_all_tips(include_unknown=True) -> list[dict]`: List of tip dicts `{'id', 'name', 'material', 'color_hex', 'icon_char', 'is_default'}`.
- `get_last_used_tip(iem_id: int) -> int | None`: Most recent `tip_id` for `iem_id` where `tip_id != 1`.
- `save_measurement(..., tip_id=1)`: Saves measurement with `tip_id`. Default 1.
- `get_reproducibility_scores(iem_id: int, tip_id: int) -> dict | None`: Returns dict with `'left'` and `'right'` channel scores or None if < 5 measurements. Each channel has `{'score', 'std_dev', 'count', 'is_preliminary'}`.
- `get_seal_history(iem_id: int, tip_id: int) -> dict`: Returns `{'left': list[dict], 'right': list[dict]}` where each record has `{'id', 'timestamp', 'delta_db', 'val_40', 'val_500', 'seal_ok', 'status'}`.

## Code Layout
- `/Users/ben/Desktop/InEarSnitch/config.py`: Configuration and offline unlock gate. Owned by M1 Worker.
- `/Users/ben/Desktop/InEarSnitch/database.py`: DatabaseManager, tables, migrations, BLOB processing. Owned by M2 Worker.
- `/Users/ben/Desktop/InEarSnitch/main.py`: Main window, bottom toolbar, header logo, measurement save flow. Owned by M3 Worker.
- `/Users/ben/Desktop/InEarSnitch/history_ui.py`: HistoryWidget, HistoryCardWidget, history load/query. Owned by M4 Worker.
- `/Users/ben/Desktop/InEarSnitch/analysis_ui.py`: AnalysisWidget, render_diagnostics, diagnostics cards. Owned by M5 Worker.
- `/Users/ben/Desktop/InEarSnitch/tests/`: Dedicated test suites and E2E harness. Owned by E2E Testing Track.
