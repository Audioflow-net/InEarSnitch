# BRIEFING — 2026-09-22T07:08:45Z

## Mission
Investigate and design the header logo/title triple-click unlock detection mechanism, dialog flow, and UI visibility update in main.py for Milestone 3.

## 🔒 My Identity
- Archetype: explorer
- Roles: investigator, analyzer, synthesizer
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m3_2
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 3 (R3 main.py ProKit Unlock Event Filter)

## 🔒 Key Constraints
- Read-only investigation — do NOT modify application source code
- Examine header logo/title in main.py
- Design robust triple-click detection (eventFilter or subclass or timestamp tracking)
- Handle unlock flow: dialog prompt -> config.unlock_prokit(code) -> success/failure feedback + update_prokit_ui_visibility()
- Ensure standard mouse events on other widgets/window controls are not degraded/blocked
- Review test coverage in tests/test_prokit_e2e.py

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: not yet

## Investigation State
- **Explored paths**:
  - `ORIGINAL_REQUEST.md`: Verified R3 unlock specifications and locked design constraints
  - `PROJECT.md`: Verified milestone decomposition and interface contracts
  - `main.py`: Identified header widgets (lines 747-752: `logo = QLabel("InEar SNITCH")`, `sublogo = QLabel("DIAGNOSTICS")`), main window class `MainWindow`, page references (`page_prof`, `page_ana`, `page_hist`), and bottom toolbar
  - `config.py`: Verified `unlock_prokit(code)`, `is_prokit_unlocked()`, `revoke_prokit()`
  - `smoke_test.py`: Verified 19/19 checks passing; confirmed critical references
  - `tests/test_prokit_e2e.py`: Analyzed `TestTier1TripleClickUnlock`, `TestTier2TripleClickBoundaries`, and `TestTier3CrossFeatureCombinations`
- **Key findings**:
  - `logo` and `sublogo` in `main.py` are local variables; need to expose `self.lbl_logo = logo`, `self.lbl_title = logo`, `self.lbl_sublogo = sublogo`.
  - In Qt, triple-click delivers `MouseButtonPress` (click 1), `MouseButtonDblClick` (click 2, replacing press), and `MouseButtonPress` (click 3). In synthetic tests (`QTest.mouseClick`), it delivers 3x `MouseButtonPress`. Filtering both `MouseButtonPress` and `MouseButtonDblClick` handles both real-world and automated tests seamlessly.
  - Sub-millisecond intervals in unit tests mean debouncing must be zero or strictly microsecond-safe, while interval timeout should reset after ~500ms (or `max(0.5, QApplication.doubleClickInterval() / 1000.0)`).
  - Installing `LogoTripleClickFilter` strictly on `self.lbl_logo` guarantees zero interference with other widgets, window controls, and canvas dragging.
  - Dialog flow using `QInputDialog.getText` and `QMessageBox.information`/`QMessageBox.warning` satisfies all prompt criteria and allows clean mocking. `ProKitUnlockDialog(QDialog)` provides styled UI option.
  - Module-level alias `InEarSnitchApp = MainWindow` fixes `AttributeError` in `test_prokit_e2e.py` line 416.
- **Unexplored areas**: None for M3 unlock event filter scope.

## Key Decisions Made
- Use dedicated `LogoTripleClickFilter(QObject)` installed on `self.lbl_logo` (and `self.lbl_sublogo`).
- Track left-click timestamps with interval comparison to reset on pauses > 0.5s.
- Trigger `on_logo_triple_clicked()` on 3rd click and consume only the 3rd click event.
- Implement `update_prokit_ui_visibility()` to toggle bottom bar combo, refresh history, and refresh diagnostics.
- Add `InEarSnitchApp = MainWindow` alias in `main.py`.

## Artifact Index
- DISPATCH.md — record of prompts received
- BRIEFING.md — situational awareness
- progress.md — liveness heartbeat
- handoff.md — final analysis and handoff report
