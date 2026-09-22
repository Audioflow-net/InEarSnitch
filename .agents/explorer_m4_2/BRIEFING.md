# BRIEFING — 2026-09-22T07:39:30Z

## Mission
Investigate HistoryCardWidget in history_ui.py, design the Tip Badge, specify ProKit unlock gating & dynamic updates, and check test_prokit_e2e.py expectations.

## 🔒 My Identity
- Archetype: explorer
- Roles: card UI & badge designer, investigator, synthesizer
- Working directory: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_2
- Original parent: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Milestone: Milestone 4 (R4 history_ui.py)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Design Tip Badge in HistoryCardWidget
- Gating by config.is_prokit_unlocked()
- Inspect test_prokit_e2e.py for assertions, attributes, styling

## Current Parent
- Conversation ID: d18b5e78-f17e-4319-bb8e-f9a56ecd2248
- Updated: 2026-09-22T07:39:30Z

## Investigation State
- **Explored paths**: `history_ui.py`, `theme.py`, `database.py`, `main.py`, `tests/test_prokit_e2e.py`, `tests/test_forensic_m3.py`, `tests/test_prokit_adversarial_ui.py`, `ORIGINAL_REQUEST.md`, `PROJECT.md`
- **Key findings**:
  - `HistoryCardWidget` layout currently lacks tip badges and seal status.
  - Sidebar width is 220px–345px; placing seal on a 3rd line in `info_layout` avoids squeezing `lbl_iem`.
  - For Unbekannt (`id=1`), badge displays `"?"` with style `#6b7280` / `#a1a1aa`, exactly matching `test_history_card_unknown_tip_badge`.
  - For known tips, badge displays `f"{icon_char} {tip_name}"` with `color_hex` and white text, matching `test_history_card_badge_display_attributes`.
  - Seal status maintains Locked Decision 2 (L and R strictly separate).
  - Aliases `tip_badge`, `lbl_tip_badge`, `lbl_tip`, `lbl_seal`, `seal_badge` provide universal attribute compatibility.
- **Unexplored areas**: None for M4 Card UI & Badge Designer scope.

## Key Decisions Made
- Designed pill badge `QLabel` for ear tips with exact color/icon mappings.
- Specified `"?"` for Unbekannt (`id=1`) and `f"{icon_char} {tip_name}"` for known tips.
- Positioned `lbl_seal` in `info_layout` below timestamp so it collapses cleanly when locked.
- Designed `update_prokit_visibility()` on card and `update_prokit_ui_visibility()` on `HistoryWidget`.

## Artifact Index
- DISPATCH.md — Dispatch message
- BRIEFING.md — Situational awareness
- progress.md — Liveness heartbeat
- handoff.md — Final handoff report
