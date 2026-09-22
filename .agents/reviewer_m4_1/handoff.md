# Milestone 4 (R4 history_ui.py) Code Review & Adversarial Challenge Report

## Review Summary

**Verdict**: **APPROVE**

---

## 1. Observation

1. **Scope and Git Inspection**:
   - Commit reviewed: `525c0a1 feat(prokit): implement tip badges and acoustic seal in history_ui.py`
   - Files changed: Exactly 1 file modified in `525c0a1`: `history_ui.py` (+350 lines, -52 lines).
   - Working tree clean (only `.agents/` metadata uncommitted).
   - Database safety: `inearsnitch.db` unchanged at exactly `16379904` bytes.

2. **Constructor and Backwards Compatibility (`HistoryCardWidget`)**:
   - Signature:
     ```python
     def __init__(
         self,
         timestamp,
         iem_name,
         side,
         parent=None,
         tip_id=1,
         tip_name="Unbekannt",
         tip_color="#6b7280",
         tip_icon="?",
         tip_material="Standard",
         seal_l=None,
         seal_r=None,
         seal_text="",
         freq=None,
         mag_l=None,
         mag_r=None,
         **kwargs
     ):
     ```
   - Legacy callers providing 3 arguments (`timestamp`, `iem_name`, `side`) or 4 arguments (`parent`) instantiate without error.
   - All tip and seal parameters have default values (`tip_id=1`, `tip_name="Unbekannt"`, `tip_color="#6b7280"`, `tip_icon="?"`).
   - `**kwargs` catches and ignores any unexpected legacy keyword arguments.

3. **Tip Badge Implementation & Styling**:
   - `lbl_tip_badge` created as `QLabel`.
   - Aliases provided: `self.tip_badge = self.lbl_tip_badge`, `self.lbl_badge = self.lbl_tip_badge`, `self.lbl_tip = self.lbl_tip_badge`.
   - For Unbekannt (`tip_id == 1` or `tip_name == "Unbekannt"`):
     - Text: `"?"`
     - Stylesheet: `"background-color: #6b7280; color: #a1a1aa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;"`
     - Tooltip: `"Ear Tip: Unbekannt"`
   - For known tips (`tip_id != 1`):
     - Text: `f"{tip_icon} {tip_name}"`
     - Stylesheet: `f"background-color: {tip_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;"`
     - Tooltip: `f"Ear Tip: {tip_name} ({tip_material})"`

4. **Locked Design Decision 2 (L and R ALWAYS separate)**:
   - Dedicated widgets: `lbl_seal_l` (Left seal status: `"L: OK"` / `"L: LEAK"`) and `lbl_seal_r` (Right seal status: `"R: OK"` / `"R: LEAK"`).
   - Dedicated summary label: `lbl_seal` (`self.seal_badge`).
   - `compute_seal_for_channel(freq, mag)` computes:
     - `val_40 = np.mean(mag[(freq >= 35.0) & (freq <= 45.0)])`
     - `val_500 = np.mean(mag[(freq >= 450.0) & (freq <= 550.0)])`
     - `delta_db = round(val_40 - val_500, 1)`
     - `status = "OK" if delta_db >= -11.8 else "LEAK"`
   - Evaluated strictly per channel (`mag_l` vs `mag_r`). **Zero cross-channel averaging**.
   - Formatted string:
     - Stereo: `"Seal: L +2.1dB | R -1.4dB"`
     - Mono Left: `"Seal L: +2.1dB"`
     - Mono Right: `"Seal R: -1.4dB"`
     - Empty / Corrupt / Missing: `""`

5. **ProKit Gate & Dynamic Visibility**:
   - Initial check: `is_unlocked = config.is_prokit_unlocked()`.
   - Visibility states:
     ```python
     self.lbl_tip_badge.setVisible(is_unlocked)
     self.lbl_seal.setVisible(is_unlocked and bool(self.seal_text))
     self.lbl_seal_l.setVisible(is_unlocked and self.seal_l_status is not None)
     self.lbl_seal_r.setVisible(is_unlocked and self.seal_r_status is not None)
     ```
   - Dynamic update method: `HistoryCardWidget.update_prokit_visibility(self, unlocked=None)`.
   - Container update method: `HistoryWidget.update_prokit_ui_visibility(self, unlocked=None)` with alias `HistoryWidget.update_prokit_visibility`.

6. **History SQL Query (`HistoryWidget.load_history`)**:
   - Query:
     ```sql
     SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r,
            iem.model_name, iem.custom_name, m.meas_name,
            COALESCE(m.tip_id, 1) AS tip_id,
            COALESCE(t.name, 'Unbekannt') AS tip_name,
            COALESCE(t.icon_char, '?') AS tip_icon,
            COALESCE(t.color_hex, '#6b7280') AS tip_color
     FROM Measurements m
     JOIN IEM_Models iem ON m.iem_id = iem.id
     LEFT JOIN TipProfiles t ON m.tip_id = t.id
     WHERE iem.musician_id = ?
     ORDER BY m.timestamp DESC LIMIT 100
     ```
   - Unpacks numpy BLOBs, invokes `compute_seal_for_channel`, populates `data_dict`, and instantiates `HistoryCardWidget`.
   - `filter_history(self)` searches `iem_name`, `timestamp`, and `tip_name`.

---

## 2. Logic Chain

1. **Backwards Compatibility Logic**:
   - Observation 2 demonstrates that all legacy calls `HistoryCardWidget(timestamp, iem_name, side)` match positional parameters 0, 1, 2. The 4th positional parameter is `parent=None`. Any subsequent parameters default cleanly. Therefore, existing tests and call sites remain 100% operational without modification.

2. **Locked Design Decision 2 Compliance Logic**:
   - Observation 4 confirms that `mag_l` and `mag_r` are fed separately into `compute_seal_for_channel`.
   - In asymmetric scenarios (e.g. L = -5.0 dB [OK], R = -15.0 dB [LEAK]), averaging would produce -10.0 dB (falsely OK). Under this implementation, L shows OK and R shows LEAK. Averaging does not occur anywhere in data or UI paths.

3. **ProKit Gate Logic**:
   - Observation 5 confirms all ProKit badges and seal labels are explicitly hidden when `config.is_prokit_unlocked()` is False. Calling `update_prokit_visibility(unlocked)` propagates dynamically to all child widgets in active history list cards without requiring a database query reload.

4. **Integrity & Code Quality Logic**:
   - No mock facades or hardcoded test returns were found. `compute_seal_for_channel` performs real numerical calculations via numpy array masking and mean. The SQL query performs a genuine SQLite `LEFT JOIN` and unpacks real IEEE 754 float64 arrays.

---

## 3. Caveats

1. **Qt Offscreen Visibility Semantics**:
   - In Qt, `widget.isVisible()` returns `True` only when all ancestors up to the window are visible and shown. When asserting widget visibility on detached widgets offscreen, `not widget.isHidden()` or calling `widget.show()` must be used.
2. **Milestone 5 Separation**:
   - `analysis_ui.py` is planned for Milestone 5 and was not modified in this milestone.

---

## 4. Conclusion & Findings

### Integrity Audit
- **Hardcoded test outputs**: NONE.
- **Dummy/facade implementations**: NONE. Real numpy DSP calculations and real SQLite queries.
- **Shortcuts / Task bypasses**: NONE.
- **Fabricated logs**: NONE.
- **Verdict**: **APPROVE**.

### Findings Summary
- **Critical**: 0
- **Major**: 0
- **Minor**: 0

### Verified Claims

| Claim | Verification Method | Result |
|---|---|---|
| Smoke test passes 19/19 | `python3 smoke_test.py` | PASS (19/19) |
| History tests pass | `pytest -v tests/test_prokit_e2e.py -k "History"` | PASS (15/15) |
| Adversarial test suites pass | `pytest -v tests/test_prokit_adversarial_ui.py tests/test_prokit_adversarial_db.py tests/test_adversarial_dsp.py` | PASS (67/67) |
| Legacy 3-arg constructor | Python headless test: `HistoryCardWidget(timestamp, iem_name, side)` | PASS |
| Tip badge styling & aliases | Inspected & asserted `tip_badge`, `lbl_badge`, `lbl_tip`, CSS colors | PASS |
| Unbekannt badge formatting | Text `?`, background `#6b7280`, color `#a1a1aa` | PASS |
| Design Decision 2 (L/R separate) | Asymmetric stereo sweep (L OK, R LEAK) - no averaging | PASS |
| Mono formatting | Mono Left: `Seal L: ...`, Mono Right: `Seal R: ...` | PASS |
| ProKit Gate visibility | Hidden when locked, visible when unlocked, dynamic toggle | PASS |
| Seal threshold boundaries | -11.7 dB (OK), -11.8 dB (OK), -11.9 dB (LEAK) | PASS |
| Production DB invariant | `ls -l inearsnitch.db` -> 16379904 bytes | PASS |

---

## 5. Verification Method

To independently verify this review:

1. **Execute Smoke Test**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   *Expected output*: `✅ ALL 19 CHECKS PASSED`.

2. **Execute E2E History Tests**:
   ```bash
   pytest -v /Users/ben/Desktop/InEarSnitch/tests/test_prokit_e2e.py -k "History"
   ```
   *Expected output*: `15 passed, 72 deselected`.

3. **Execute Adversarial Test Suites**:
   ```bash
   pytest -v /Users/ben/Desktop/InEarSnitch/tests/test_prokit_adversarial_ui.py /Users/ben/Desktop/InEarSnitch/tests/test_prokit_adversarial_db.py /Users/ben/Desktop/InEarSnitch/tests/test_adversarial_dsp.py
   ```
   *Expected output*: `67 passed`.

4. **Verify Database Size**:
   ```bash
   ls -l /Users/ben/Desktop/InEarSnitch/inearsnitch.db
   ```
   *Expected output*: Exactly `16379904` bytes.

5. **Standalone HistoryCardWidget & ProKit Gate Verification**:
   ```bash
   python3 -c "
   import os
   os.environ['QT_QPA_PLATFORM'] = 'offscreen'
   from PySide6.QtWidgets import QApplication
   from unittest.mock import patch
   import numpy as np
   import config
   from history_ui import HistoryCardWidget

   app = QApplication.instance() or QApplication([])

   # 1. Backwards compatibility
   c1 = HistoryCardWidget('2026-09-22 10:00:00', 'Moondrop Aria', 'Left')
   assert c1.tip_id == 1 and c1.tip_name == 'Unbekannt' and c1.lbl_tip_badge.text() == '?'
   assert c1.tip_badge is c1.lbl_tip_badge and c1.lbl_badge is c1.lbl_tip_badge and c1.lbl_tip is c1.lbl_tip_badge

   # 2. Asymmetric stereo (No averaging)
   freqs = np.linspace(20.0, 20000.0, 2000)
   ml, mr = np.full_like(freqs, 90.0), np.full_like(freqs, 90.0)
   ml[(freqs >= 35.0) & (freqs <= 45.0)] = 85.0   # -5.0 dB -> OK
   mr[(freqs >= 35.0) & (freqs <= 45.0)] = 75.0   # -15.0 dB -> LEAK
   c2 = HistoryCardWidget('2026-09-22', 'Test IEM', 'Stereo', freq=freqs, mag_l=ml, mag_r=mr)
   assert c2.seal_l_status == 'OK' and c2.seal_r_status == 'LEAK'
   assert c2.seal_text == 'Seal: L -5.0dB | R -15.0dB'

   # 3. Gate toggle
   with patch.object(config, 'is_prokit_unlocked', return_value=False):
       c3 = HistoryCardWidget('2026-09-22', 'Gated', 'Stereo', freq=freqs, mag_l=ml, mag_r=mr)
       assert c3.lbl_tip_badge.isHidden() and c3.lbl_seal.isHidden()
       c3.update_prokit_visibility(unlocked=True)
       assert not c3.lbl_tip_badge.isHidden() and not c3.lbl_seal.isHidden()
   print('Verification complete: ALL PASSED')
   "
   ```
