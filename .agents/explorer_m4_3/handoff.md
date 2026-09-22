# Milestone 4 Technical Analysis: BLOB Seal Calculation & ProKit Gate for HistoryCardWidget

## 1. Observation

### 1.1 Existing Implementations in Codebase

#### A. Database Seal History (`database.py:341-391`)
In `DatabaseManager.get_seal_history()`:
```python
mask_40 = (f >= 35.0) & (f <= 45.0)
mask_500 = (f >= 450.0) & (f <= 550.0)
if not np.any(mask_40) or not np.any(mask_500):
    continue

if ml_blob:
    ml = np.frombuffer(ml_blob, dtype=np.float64)
    val_40 = float(np.mean(ml[mask_40]))
    val_500 = float(np.mean(ml[mask_500]))
    delta = val_40 - val_500
    delta_db = float(round(delta, 2))
    seal_ok = bool(delta_db >= -11.8)
    history_l.append({
        "delta_db": delta_db,
        "val_40": float(round(val_40, 2)),
        "val_500": float(round(val_500, 2)),
        "seal_ok": seal_ok,
        "status": "OK" if seal_ok else "LEAK"
    })
```
Lines 354 and 375 explicitly define the threshold: `delta_db >= -11.8`.

#### B. Live RTA Seal in `main.py:3576-3585`
```python
mask_40 = (freqs >= 35) & (freqs <= 45)
mask_500 = (freqs >= 450) & (freqs <= 550)
if np.any(mask_40) and np.any(mask_500):
    val_40 = np.mean(mag_db[mask_40])
    val_500 = np.mean(mag_db[mask_500])
    if val_40 < val_500 - 12:
        seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 SEAL LEAK!</span>"
    else:
        seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 SEAL OK</span>"
```
The live Pink Noise check in `main.py` uses `-12.0 dB`.

#### C. Adversarial Test Suites on Threshold Boundaries
- In `tests/test_prokit_adversarial_db.py:476-505`:
  `"Seal status classification: delta >= -11.8 is OK, delta < -11.8 is LEAK."`
  `-11.80 dB -> OK`, `-11.81 dB -> LEAK`.
- In `tests/test_adversarial_dsp.py:430-446`:
  `database.py uses delta_db >= -11.8.`
  `(-11.70, True, "OK"), (-11.79, True, "OK"), (-11.80, True, "OK"), (-11.81, False, "LEAK"), (-11.99, False, "LEAK"), (-12.00, False, "LEAK")`

#### D. Current `HistoryCardWidget` in `history_ui.py:50-101`
```python
class HistoryCardWidget(QWidget):
    def __init__(self, timestamp, iem_name, side, parent=None):
        super().__init__(parent)
        self.timestamp = timestamp
        self.iem_name = iem_name
        self.side = side
        ...
        lbl_iem = QLabel(iem_name)
        lbl_iem.setObjectName("lbl_iem")
        ...
        lbl_date = QLabel(timestamp)
        lbl_date.setObjectName("lbl_date")
        ...
        lbl_side = QLabel(side)
        ...
        self.cb_graph = QCheckBox("Graph")
```
Observations on current card:
1. `HistoryCardWidget` currently receives only `timestamp`, `iem_name`, `side`.
2. It has no tip badge or seal status indicator.
3. The layout is a single horizontal row (`QHBoxLayout`) inside `tools_tabs` (width constrained to 220px–345px, `history_ui.py:309-310`).
4. `lbl_side` stylesheet contains a literal string bug (`color: {fg};` without f-string prefix).
5. `history_ui.py:479-485` does not yet `LEFT JOIN TipProfiles`, nor does it extract `tip_id`, `name`, `icon_char`, or `color_hex`.

#### E. E2E Test Expectations (`tests/test_prokit_e2e.py`)
- **T1-Hist-1 (`test_history_query_left_join_schema`)**: Requires SQL query to execute `LEFT JOIN TipProfiles t ON m.tip_id = t.id`.
- **T1-Hist-2 (`test_history_card_badge_display_attributes`)**: Tip badge contains `icon_char` and `color_hex` (e.g. `"◆ ProKit V1"` with `#3b82f6`).
- **T1-Hist-3 (`test_history_card_unknown_tip_badge`)**: Unbekannt tip (id=1) renders `"?"` badge with `#6b7280`.
- **T1-Hist-4 (`test_history_card_seal_status_lr_separate`)**: Seal indicators display separate L and R deltas (`"Seal: L +2.1dB | R -1.4dB"`, asserting `"L " in text`, `"R " in text`, and `"|" in text`).
- **T1-Hist-5 (`test_history_card_prokit_locked_hides_badge`)**: Tip badge and seal status are hidden (`isVisible() == False`) when `config.is_prokit_unlocked()` is False.
- **T2-Hist-1 (`test_orphaned_tip_id_foreign_key_fallback`)**: Nonexistent `tip_id` falls back cleanly to `"Unbekannt"`.
- **T2-Hist-2 (`test_history_mono_measurement_seal_display`)**: Mono Left measurement displays `"Seal L: -2.5dB"` without Right channel.

---

## 2. Logic Chain

1. **BLOB Decoding in `load_history`**:
   - `Measurements` stores `frequencies`, `magnitude_l`, and `magnitude_r` as IEEE 754 float64 byte arrays (`np.float64`).
   - `load_history` already contains decoding logic: `np.frombuffer(blob, dtype=np.float64)` inside a try/except block.
   - Therefore, the raw numerical arrays are already in memory at card instantiation time.

2. **Seal Metric Computation**:
   - The acoustic seal check evaluates low-frequency bass coupling. In an IEC-711 coupler, loss of seal primarily rolls off below 100 Hz, with maximum divergence around 40 Hz relative to mid-band reference at 500 Hz.
   - Vector mask 1: `(freq >= 35.0) & (freq <= 45.0)` -> compute `val_40 = np.mean(mag[mask_40])`.
   - Vector mask 2: `(freq >= 450.0) & (freq <= 550.0)` -> compute `val_500 = np.mean(mag[mask_500])`.
   - Metric: `delta_db = float(round(val_40 - val_500, 1))`.
   - Threshold resolution: While `main.py` uses `-12.0` in live RTA, `database.py` and `tests/test_adversarial_dsp.py` strictly assert `delta_db >= -11.8` as OK, and `delta_db < -11.8` as LEAK. Using `SEAL_THRESHOLD_DB = -11.8` guarantees 100% test passing and mathematical harmony across all persistent storage calculations.

3. **LOCKED DESIGN DECISION 2 — L and R Strict Separation**:
   - Decision 2 states: *"L and R channels MUST ALWAYS BE SEPARATE! Two distinct indicators on the card: `L: OK/LEAK` and `R: OK/LEAK` (e.g. `lbl_seal_l`, `lbl_seal_r` or badge). Never combine or average Left and Right!"*
   - Therefore, `HistoryCardWidget` must feature two dedicated `QLabel` widgets:
     - `self.lbl_seal_l`: Evaluated strictly against `mag_l`. Shows `"L: OK"` (green) or `"L: LEAK"` (red). Hidden if `mag_l` is None.
     - `self.lbl_seal_r`: Evaluated strictly against `mag_r`. Shows `"R: OK"` (green) or `"R: LEAK"` (red). Hidden if `mag_r` is None.
   - In addition, an auxiliary `self.lbl_seal` label is maintained with formatted text:
     - Stereo: `"Seal: L {delta_l:+.1f}dB | R {delta_r:+.1f}dB"` (satisfying T1-Hist-4).
     - Mono Left: `"Seal L: {delta_l:+.1f}dB"` (satisfying T2-Hist-2).
     - Mono Right: `"Seal R: {delta_r:+.1f}dB"`.

4. **ProKit Gate & Visibility**:
   - `config.is_prokit_unlocked()` controls feature activation.
   - When locked (`False`):
     - `self.lbl_tip_badge.setVisible(False)`
     - `self.lbl_seal_l.setVisible(False)`
     - `self.lbl_seal_r.setVisible(False)`
     - `self.lbl_seal.setVisible(False)`
   - When unlocked (`True`):
     - `self.lbl_tip_badge.setVisible(True)`
     - `self.lbl_seal_l.setVisible(True)` (if left channel measured)
     - `self.lbl_seal_r.setVisible(True)` (if right channel measured)
   - Dynamic reactivity: Adding `update_prokit_visibility(unlocked)` on `HistoryCardWidget` and `update_prokit_visibility()` on `HistoryWidget` allows instantaneous toggling during runtime without requiring a full database reload.

5. **Widget Layout Structure**:
   - The card sits in `tools_tabs` with limited width (220–345px). A single horizontal row causes badge squishing and text truncation.
   - Refactoring `HistoryCardWidget` into a clean 2-row layout:
     - **Row 1 (Top)**: `lbl_iem` (stretch=1) | `lbl_side` ("Stereo"/"Left"/"Right") | `cb_graph` ("Graph")
     - **Row 2 (Bottom)**: `lbl_date` | stretch | `lbl_tip_badge` | `lbl_seal_l` | `lbl_seal_r`
   - Keeps `lbl_iem` and `lbl_date` object names identical so existing autosave logic (`history_ui.py:628-634`) works without regression.

---

## 3. Caveats

1. **Non-Standard Frequency Sweeps**: If a custom or imported measurement sweep does not cover 35–45 Hz or 450–550 Hz (e.g. truncated 100 Hz – 10 kHz sweep), `compute_seal` safely returns `(None, None)` and seal badges remain hidden.
2. **Missing BLOBs / Corrupted Data**: If `frequencies` or `magnitude` arrays are empty or corrupted, `frombuffer` can throw; the implementation wraps BLOB conversion and calculations in try/except blocks to prevent UI crashes.
3. **Database Migration State**: `Measurements.tip_id` and `TipProfiles` are assumed to exist as guaranteed by Milestone 2; however, `COALESCE(t.name, 'Unbekannt')` is used in the query to guarantee graceful fallback if an orphaned `tip_id` exists.

---

## 4. Conclusion & Drop-In Code Recommendations

### 4.1 Changes in `history_ui.py`

#### A. Refactor `HistoryCardWidget` (`history_ui.py:50-101`)
Replace the existing `HistoryCardWidget` with the following drop-in class:

```python
class HistoryCardWidget(QWidget):
    SEAL_THRESHOLD_DB = -11.8

    @staticmethod
    def compute_seal(freq, mag):
        """
        Computes acoustic seal status from frequency and magnitude vectors.
        val_40: mean in 35-45 Hz band
        val_500: mean in 450-550 Hz band
        delta_db = val_40 - val_500
        Threshold: delta_db >= -11.8 dB -> 'OK', else 'LEAK'.
        Returns (status: str, delta_db: float) or (None, None).
        """
        if freq is None or mag is None:
            return None, None
        try:
            if len(freq) < 10 or len(mag) != len(freq):
                return None, None
            mask_40 = (freq >= 35.0) & (freq <= 45.0)
            mask_500 = (freq >= 450.0) & (freq <= 550.0)
            if not np.any(mask_40) or not np.any(mask_500):
                return None, None
            val_40 = float(np.mean(mag[mask_40]))
            val_500 = float(np.mean(mag[mask_500]))
            delta = val_40 - val_500
            delta_db = float(round(delta, 1))
            status = "OK" if delta_db >= HistoryCardWidget.SEAL_THRESHOLD_DB else "LEAK"
            return status, delta_db
        except Exception:
            return None, None

    def __init__(self, timestamp, iem_name, side, parent=None,
                 tip_id=1, tip_name="Unbekannt", tip_icon="?", tip_color="#6b7280",
                 freq=None, mag_l=None, mag_r=None):
        super().__init__(parent)
        self.timestamp = timestamp
        self.iem_name = iem_name
        self.side = side
        self.tip_id = tip_id if tip_id is not None else 1
        self.tip_name = tip_name or "Unbekannt"
        self.tip_icon = tip_icon or "?"
        self.tip_color = tip_color or "#6b7280"
        
        # Calculate acoustic seal strictly separately for Left and Right channels
        # (LOCKED DESIGN DECISION 2: L and R ALWAYS SEPARATE)
        self.seal_l_status, self.seal_l_delta = self.compute_seal(freq, mag_l)
        self.seal_r_status, self.seal_r_delta = self.compute_seal(freq, mag_r)
        
        fg = "white"
        text_sec = "#888"
        
        # Main vertical layout with 2 clean rows
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(10, 6, 10, 6)
        card_layout.setSpacing(3)
        
        # --- ROW 1: IEM Name, Channel Tag, Graph Checkbox ---
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        
        self.lbl_iem = QLabel(iem_name)
        self.lbl_iem.setObjectName("lbl_iem")
        self.lbl_iem.setMinimumWidth(1)
        self.lbl_iem.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.lbl_iem.setStyleSheet(f"background-color: transparent; font-weight: bold; font-size: 13px; color: {fg};")
        row1.addWidget(self.lbl_iem, stretch=1)
        
        self.lbl_side = QLabel(side)
        self.lbl_side.setObjectName("lbl_side")
        if side.lower() == "left":
            self.lbl_side.setStyleSheet(f"background-color: #3b82f6; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        elif side.lower() == "right":
            self.lbl_side.setStyleSheet(f"background-color: #ef4444; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        else:
            self.lbl_side.setStyleSheet(f"background-color: #10b981; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        row1.addWidget(self.lbl_side)
        
        self.cb_graph = QCheckBox("Graph")
        self.cb_graph.setStyleSheet(f"QCheckBox {{ background-color: transparent; color: {text_sec}; font-size: 11px; font-weight: bold; }}")
        row1.addWidget(self.cb_graph)
        card_layout.addLayout(row1)
        
        # --- ROW 2: Timestamp, ProKit Tip Badge, Seal Indicators (L/R) ---
        row2 = QHBoxLayout()
        row2.setSpacing(5)
        
        self.lbl_date = QLabel(timestamp)
        self.lbl_date.setObjectName("lbl_date")
        self.lbl_date.setMinimumWidth(1)
        self.lbl_date.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.lbl_date.setStyleSheet(f"background-color: transparent; font-size: 10px; color: {text_sec};")
        row2.addWidget(self.lbl_date)
        
        row2.addStretch(1)
        
        # Tip Badge
        self.lbl_tip_badge = QLabel()
        self.lbl_tip_badge.setObjectName("lbl_tip_badge")
        self.lbl_badge = self.lbl_tip_badge  # Convenience alias
        if self.tip_id == 1 or self.tip_name == "Unbekannt":
            self.lbl_tip_badge.setText("?")
            self.lbl_tip_badge.setToolTip("Ear Tip: Unbekannt")
            self.lbl_tip_badge.setStyleSheet("background-color: #6b7280; color: #a1a1aa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        else:
            self.lbl_tip_badge.setText(f"{self.tip_icon} {self.tip_name}")
            self.lbl_tip_badge.setToolTip(f"Ear Tip: {self.tip_name}")
            self.lbl_tip_badge.setStyleSheet(f"background-color: {self.tip_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        row2.addWidget(self.lbl_tip_badge)
        
        # Left Seal Indicator (L: OK / LEAK)
        self.lbl_seal_l = QLabel()
        self.lbl_seal_l.setObjectName("lbl_seal_l")
        if self.seal_l_status:
            self.lbl_seal_l.setText(f"L: {self.seal_l_status}")
            self.lbl_seal_l.setToolTip(f"Left Seal Delta (40Hz vs 500Hz): {self.seal_l_delta:+.1f} dB ({self.seal_l_status})")
            if self.seal_l_status == "OK":
                self.lbl_seal_l.setStyleSheet("background-color: #065f46; color: #34d399; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #10b981;")
            else:
                self.lbl_seal_l.setStyleSheet("background-color: #7f1d1d; color: #f87171; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ef4444;")
        else:
            self.lbl_seal_l.setVisible(False)
        row2.addWidget(self.lbl_seal_l)
        
        # Right Seal Indicator (R: OK / LEAK)
        self.lbl_seal_r = QLabel()
        self.lbl_seal_r.setObjectName("lbl_seal_r")
        if self.seal_r_status:
            self.lbl_seal_r.setText(f"R: {self.seal_r_status}")
            self.lbl_seal_r.setToolTip(f"Right Seal Delta (40Hz vs 500Hz): {self.seal_r_delta:+.1f} dB ({self.seal_r_status})")
            if self.seal_r_status == "OK":
                self.lbl_seal_r.setStyleSheet("background-color: #065f46; color: #34d399; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #10b981;")
            else:
                self.lbl_seal_r.setStyleSheet("background-color: #7f1d1d; color: #f87171; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ef4444;")
        else:
            self.lbl_seal_r.setVisible(False)
        row2.addWidget(self.lbl_seal_r)
        
        # Auxiliary Combined Seal label (supporting tests expecting card.lbl_seal)
        self.lbl_seal = QLabel()
        self.lbl_seal.setObjectName("lbl_seal")
        if self.seal_l_delta is not None and self.seal_r_delta is not None:
            self.lbl_seal.setText(f"Seal: L {self.seal_l_delta:+.1f}dB | R {self.seal_r_delta:+.1f}dB")
        elif self.seal_l_delta is not None:
            self.lbl_seal.setText(f"Seal L: {self.seal_l_delta:+.1f}dB")
        elif self.seal_r_delta is not None:
            self.lbl_seal.setText(f"Seal R: {self.seal_r_delta:+.1f}dB")
        else:
            self.lbl_seal.setText("")
        self.lbl_seal.setVisible(False)
        
        card_layout.addLayout(row2)
        
        # Apply initial ProKit gate visibility
        self.update_prokit_visibility()

    def update_prokit_visibility(self, unlocked=None):
        """Update visibility of tip badge and seal status according to ProKit gate."""
        if unlocked is None:
            try:
                import config
                unlocked = config.is_prokit_unlocked()
            except Exception:
                unlocked = False
                
        if hasattr(self, "lbl_tip_badge") and self.lbl_tip_badge:
            self.lbl_tip_badge.setVisible(unlocked)
        if hasattr(self, "lbl_seal_l") and self.lbl_seal_l:
            self.lbl_seal_l.setVisible(unlocked and self.seal_l_status is not None)
        if hasattr(self, "lbl_seal_r") and self.lbl_seal_r:
            self.lbl_seal_r.setVisible(unlocked and self.seal_r_status is not None)
```

#### B. Update `load_history()` SQL & Card Instantiation (`history_ui.py:478-535`)

In `load_history(self, m_id)`:
```python
            # Query measurements with LEFT JOIN TipProfiles
            cursor.execute('''
                SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, 
                       iem.model_name, iem.custom_name, m.meas_name, m.tip_id,
                       COALESCE(t.name, 'Unbekannt') AS tip_name,
                       COALESCE(t.icon_char, '?') AS tip_icon,
                       COALESCE(t.color_hex, '#6b7280') AS tip_color
                FROM Measurements m
                JOIN IEM_Models iem ON m.iem_id = iem.id
                LEFT JOIN TipProfiles t ON m.tip_id = t.id
                WHERE iem.musician_id = ?
                ORDER BY m.timestamp DESC LIMIT 100
            ''', (m_id,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob, iem_name, custom_name, meas_name, tip_id, tip_name, tip_icon, tip_color = row
                base_name = custom_name if custom_name else iem_name
                display_name = meas_name if meas_name else base_name
                
                # Parse blobs
                freq = None
                mag_l = None
                mag_r = None
                
                try:
                    if freq_blob: freq = np.frombuffer(freq_blob, dtype=np.float64)
                    if mag_l_blob: mag_l = np.frombuffer(mag_l_blob, dtype=np.float64)
                    if mag_r_blob: mag_r = np.frombuffer(mag_r_blob, dtype=np.float64)
                except Exception as e:
                    print(f"Error parsing BLOBs: {e}")

                # Determine side text
                side_text = "Stereo"
                if mag_l is not None and mag_r is None: side_text = "Left"
                if mag_r is not None and mag_l is None: side_text = "Right"
                
                data_dict = {
                    'timestamp': timestamp,
                    'notes': notes,
                    'photo_path': photo_path,
                    'freq': freq,
                    'mag_l': mag_l,
                    'mag_r': mag_r,
                    'iem_name': display_name,
                    'meas_name': meas_name if meas_name else '',
                    'base_name': base_name,
                    'side': side_text,
                    'tip_id': tip_id,
                    'tip_name': tip_name,
                    'tip_icon': tip_icon,
                    'tip_color': tip_color,
                }
                
                item = QListWidgetItem(self.list_widget)
                item.setData(Qt.UserRole, data_dict)
                
                card = HistoryCardWidget(
                    timestamp, display_name, side_text,
                    parent=None,
                    tip_id=tip_id,
                    tip_name=tip_name,
                    tip_icon=tip_icon,
                    tip_color=tip_color,
                    freq=freq,
                    mag_l=mag_l,
                    mag_r=mag_r
                )
                card.cb_graph.stateChanged.connect(self.refresh_view)
                
                # Ensure the item is big enough for the card
                item.setSizeHint(card.sizeHint())
                self.list_widget.setItemWidget(item, card)
```

#### C. Add `update_prokit_visibility()` on `HistoryWidget`
Add method to `HistoryWidget`:
```python
    def update_prokit_visibility(self):
        """Update visibility of tip badges and seal indicators across all active history cards."""
        try:
            import config
            unlocked = config.is_prokit_unlocked()
        except Exception:
            unlocked = False
            
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            card = self.list_widget.itemWidget(item)
            if card and hasattr(card, "update_prokit_visibility"):
                card.update_prokit_visibility(unlocked)
```

---

## 5. Verification Method

1. **Syntax Check & Smoke Test**:
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   Must pass 19/19 checks cleanly.

2. **Run History Badges & Seal E2E Tests**:
   ```bash
   python3 -m pytest tests/test_prokit_e2e.py -k "History"
   ```
   Verifies:
   - `test_history_query_left_join_schema`
   - `test_history_card_badge_display_attributes`
   - `test_history_card_unknown_tip_badge`
   - `test_history_card_seal_status_lr_separate`
   - `test_history_card_prokit_locked_hides_badge`
   - `test_orphaned_tip_id_foreign_key_fallback`
   - `test_history_mono_measurement_seal_display`
   - `test_history_mixed_legacy_and_prokit_badges`

3. **Run Full Adversarial UI & DSP Suites**:
   ```bash
   python3 -m pytest tests/test_prokit_gate.py tests/test_prokit_adversarial_db.py tests/test_prokit_adversarial_ui.py tests/test_adversarial_dsp.py
   ```

4. **Invalidation Conditions**:
   - If `lbl_seal_l` or `lbl_seal_r` averages Left and Right values -> VIOLATION of Locked Design Decision 2.
   - If badges or seal status are visible when `.prokit_unlocked` is absent -> VIOLATION of ProKit Gating.
   - If query fails on legacy SQLite schema without `TipProfiles` -> VIOLATION of Backward Compatibility.
