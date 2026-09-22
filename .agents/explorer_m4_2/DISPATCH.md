## 2026-09-22T07:34:58Z
You are M4 Card UI & Badge Designer for Milestone 4 (R4 history_ui.py) in the InEarSnitch ProKit Tip-Tracking project.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_2

MANDATORY: Read the authoritative user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md
Also read:
- /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1/PROJECT.md
- /Users/ben/Desktop/InEarSnitch/history_ui.py
- /Users/ben/Desktop/InEarSnitch/theme.py
- /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py

Your mission:
1. Examine `HistoryCardWidget` in `history_ui.py`:
   - Inspect the card layout, existing labels, and styling.
   - Design the Tip Badge:
     - Badge display: e.g. `QLabel` displaying `f"{icon_char} {tip_name}"` or pill badge.
     - For Unbekannt (`id=1` or NULL): grey badge displaying `? Unbekannt` or `?`.
     - For known tips (ProKit V1, V2, Standard Foam, Kein Aufsatz): styled with `color_hex` and `icon_char`.
     - Attribute name: check if tests look for `card.tip_badge`, `card.lbl_tip`, or similar.
2. Gating by `config.is_prokit_unlocked()`:
   - What should the card show when ProKit is unlocked vs locked?
   - Ensure dynamic updates when `update_prokit_ui_visibility()` is called.
3. Review `tests/test_prokit_e2e.py` for exact widget references and styling assertions.

Write your report to `/Users/ben/Desktop/InEarSnitch/.agents/explorer_m4_2/handoff.md` and notify parent when done.
