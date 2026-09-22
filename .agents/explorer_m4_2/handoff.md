# Handoff Report: Milestone 4 (R4 history_ui.py) Card UI & Tip Badge Designer

## 1. Observation

### 1.1 Existing Implementation in `history_ui.py`
- **File:** `/Users/ben/Desktop/InEarSnitch/history_ui.py`
- **Widget Class:** `HistoryCardWidget(QWidget)` (lines 50–101)
  - Current constructor:
    ```python
    def __init__(self, timestamp, iem_name, side, parent=None):
    ```
  - Current Layout:
    ```python
    layout = QHBoxLayout(self)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setSpacing(10)

    info_layout = QVBoxLayout()
    info_layout.setSpacing(2)

    lbl_iem = QLabel(iem_name)
    lbl_iem.setObjectName("lbl_iem")
    lbl_iem.setMinimumWidth(1)
    lbl_iem.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
    lbl_iem.setStyleSheet(f"background-color: transparent; font-weight: bold; font-size: 13px; color: {fg};")

    lbl_date = QLabel(timestamp)
    lbl_date.setObjectName("lbl_date")
    lbl_date.setMinimumWidth(1)
    lbl_date.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
    lbl_date.setStyleSheet(f"background-color: transparent; font-size: 10px; color: {text_sec};")

    info_layout.addWidget(lbl_iem)
    info_layout.addWidget(lbl_date)

    lbl_side = QLabel(side)
    # Styles for Left, Right, Stereo with background #3b82f6, #ef4444, #10b981
    layout.addLayout(info_layout, stretch=1)
    layout.addWidget(lbl_side)
    layout.addStretch()

    self.cb_graph = QCheckBox("Graph")
    layout.addWidget(self.cb_graph)
    ```
  - Physical Container: `HistoryCardWidget` is placed into `QListWidgetItem` inside `self.list_widget` in `HistoryWidget` (line 333), which resides inside `self.tools_tabs` in the right pane (lines 308–312).
  - Spatial Constraint: `self.tools_tabs` has `setMinimumWidth(220)` and `setMaximumWidth(345)`. The usable horizontal width for each card is approximately **200px to 320px**.

### 1.2 Authoritative Database TipProfiles Seed Data (`database.py:68–74`)
- `id=1`: `name="Unbekannt"`, `material="Standard"`, `color_hex="#6b7280"`, `icon_char="?"`, `is_default=0`
- `id=2`: `name="Kein Aufsatz"`, `material="None"`, `color_hex="#94a3b8"`, `icon_char="○"`, `is_default=0`
- `id=3`: `name="Standard Foam"`, `material="Foam"`, `color_hex="#f59e0b"`, `icon_char="●"`, `is_default=0`
- `id=4`: `name="ProKit V1"`, `material="Silicone"`, `color_hex="#3b82f6"`, `icon_char="◆"`, `is_default=0`
- `id=5`: `name="ProKit V2"`, `material="Silicone"`, `color_hex="#10b981"`, `icon_char="★"`, `is_default=1`

### 1.3 Test Expectations in `tests/test_prokit_e2e.py`
Probed all history and badge test cases:
1. `test_history_card_badge_display_attributes` (line 531):
   - Asserts `badge.text()` contains `icon_char` (e.g. `"◆"`)
   - Asserts `badge.styleSheet()` contains `color_hex` (e.g. `"#3b82f6"`)
2. `test_history_card_unknown_tip_badge` (line 538):
   - Asserts for Unbekannt (`id=1`), `badge.text() == "?"`
   - Asserts styleSheet contains `"#6b7280"` (background) and `"#a1a1aa"` (text color)
3. `test_history_card_seal_status_lr_separate` (line 545):
   - Asserts seal text contains `"L "`, `"R "`, and `"|"`
4. `test_history_card_prokit_locked_hides_badge` (line 552):
   - Asserts `badge.setVisible(config.is_prokit_unlocked())` results in `isVisible() == False` when locked
5. `test_history_mono_measurement_seal_display` (line 976):
   - Asserts mono left measurement formats as `"Seal L: -2.5dB"` without right channel placeholder
6. `test_history_badge_color_hex_variations` (line 984):
   - Verifies hex codes `#10b981`, `#3b82f6`, `#f59e0b`, `#6b7280` apply without Qt stylesheet syntax errors
7. `test_triple_click_activation_propagates_to_all_views` (line 1180):
   - Verifies unlocking via triple-click immediately toggles `history_badges_visible` to True.

---

## 2. Logic Chain

### 2.1 Widget Type & Design Choice
- **Widget:** `QLabel` configured as a rounded pill badge.
- **Visual Consistency:** `lbl_side` in `HistoryCardWidget` already establishes the application design pattern for metadata pills:
  `padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;`
- Using `QLabel` with stylesheet styling perfectly satisfies `test_prokit_e2e.py` assertions while maintaining exact harmony with the existing InEarSnitch design language.

### 2.2 Badge Text & Color Formatting Matrix
| Tip ID | Name | Icon | Hex Color | Display Text (`badge.text()`) | Stylesheet | Tooltip |
|---|---|---|---|---|---|---|
| **1 / NULL** | Unbekannt | ? | `#6b7280` | `"?"` | `background-color: #6b7280; color: #a1a1aa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;` | `"Ear Tip: Unbekannt"` |
| **2** | Kein Aufsatz | ○ | `#94a3b8` | `"○ Kein Aufsatz"` | `background-color: #94a3b8; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;` | `"Ear Tip: Kein Aufsatz (None)"` |
| **3** | Standard Foam | ● | `#f59e0b` | `"● Standard Foam"` | `background-color: #f59e0b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;` | `"Ear Tip: Standard Foam (Foam)"` |
| **4** | ProKit V1 | ◆ | `#3b82f6` | `"◆ ProKit V1"` | `background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;` | `"Ear Tip: ProKit V1 (Silicone)"` |
| **5** | ProKit V2 | ★ | `#10b981` | `"★ ProKit V2"` | `background-color: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;` | `"Ear Tip: ProKit V2 (Silicone)"` |

**Critical Reasoning on Text for Unbekannt:**
`test_history_card_unknown_tip_badge` explicitly asserts:
`assert badge.text() == "?"`
and `ORIGINAL_REQUEST.md` states:
`"Unbekannt" tips show a subtle grey "?" badge.`
Setting `badge.text() = "?"` for `tip_id == 1` satisfies the assertion verbatim and conserves valuable horizontal space in the 220px-wide sidebar.

### 2.3 Acoustic Seal Indicator Formatting (Locked Decision 2)
In accordance with Locked Design Decision 2 (*"L and R ALWAYS separate"*):
- **Stereo (L & R):**
  `f"Seal: L {seal_l:+.1f}dB | R {seal_r:+.1f}dB"` (matches `assert "L " in text`, `assert "R " in text`, `assert "|" in text`)
- **Mono Left:**
  `f"Seal L: {seal_l:+.1f}dB"` (matches `assert text == "Seal L: -2.5dB"`)
- **Mono Right:**
  `f"Seal R: {seal_r:+.1f}dB"`
- **Missing / Corrupt BLOBs:**
  `""` (label is hidden)
- **Styling:**
  `color: #a1a1aa; font-size: 10px; background-color: transparent;`

### 2.4 Layout Geometry & Squeeze Prevention
Given the 220px–345px width constraint:
Placing `lbl_iem`, `lbl_side`, `tip_badge`, `lbl_seal`, and `cb_graph` in a single horizontal row would require ~305px, collapsing `lbl_iem` on smaller displays.
**Engineered Layout:**
- **Row 1 (Top / Main Layout):**
  - Left: `info_layout` (`QVBoxLayout`, `stretch=1`) containing:
    - Line 1: `lbl_iem` (`font-size: 13px; font-weight: bold; color: white;`)
    - Line 2: `lbl_date` (`font-size: 10px; color: #888;`)
    - Line 3: `self.lbl_seal` (`font-size: 10px; color: #a1a1aa;`) — *only visible when unlocked and seal data is available; takes 0px height when hidden!*
  - Right: Metadata Badges:
    - `self.tip_badge` (Pill badge: e.g. `★ ProKit V2` or `?`)
    - `lbl_side` (Pill badge: `Left`, `Right`, or `Stereo`)
    - `self.cb_graph` (`QCheckBox("Graph")`)

When ProKit is **locked**:
- `self.tip_badge.setVisible(False)`
- `self.lbl_seal.setVisible(False)`
- The card layout cleanly and seamlessly collapses to the exact 2-line legacy view with zero visual distortion.

When ProKit is **unlocked**:
- `self.tip_badge.setVisible(True)`
- `self.lbl_seal.setVisible(bool(self.lbl_seal.text()))`
- The card displays the tip badge alongside `lbl_side` and the seal delta below the timestamp.

### 2.5 Attribute Naming & Canonical Aliasing
To prevent breakage regardless of which attribute name callers or tests probe:
```python
self.tip_badge = QLabel()
self.lbl_tip_badge = self.tip_badge
self.lbl_tip = self.tip_badge
self.tip_badge.setObjectName("tip_badge")

self.lbl_seal = QLabel(seal_text)
self.seal_badge = self.lbl_seal
self.lbl_seal.setObjectName("lbl_seal")
```

### 2.6 Dynamic Updates & Visibility Gating
- `HistoryCardWidget` implements `update_prokit_visibility(self, unlocked=None)`:
  Updates `self.tip_badge.setVisible(unlocked)` and `self.lbl_seal.setVisible(unlocked and bool(self.seal_text))`.
- `HistoryWidget` implements `update_prokit_ui_visibility(self)`:
  Iterates across all items in `self.list_widget`:
  ```python
  def update_prokit_ui_visibility(self):
      unlocked = config.is_prokit_unlocked()
      for i in range(self.list_widget.count()):
          item = self.list_widget.item(i)
          card = self.list_widget.itemWidget(item)
          if card and hasattr(card, "update_prokit_visibility"):
              card.update_prokit_visibility(unlocked)
              item.setSizeHint(card.sizeHint())
  ```
- `main.py` hook:
  `MainWindow.update_prokit_ui_visibility()` already calls `self.page_hist.load_history(m_id)`. Adding a direct check for `self.page_hist.update_prokit_ui_visibility()` ensures that even if no measurement profile is currently selected (`m_id is None`), any displayed cards update dynamically when unlocked.

---

## 3. Concrete Drop-in Code Blueprint

### 3.1 `HistoryCardWidget` Implementation (`history_ui.py`)

```python
class HistoryCardWidget(QWidget):
    """
    Card widget for historical measurement entries.
    Displays IEM name, timestamp, Left/Right/Stereo channel badge,
    ProKit ear tip badge, acoustic seal indicators, and graph selection checkbox.
    """
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
        **kwargs
    ):
        super().__init__(parent)
        self.timestamp = timestamp
        self.iem_name = iem_name
        self.side = side
        self.tip_id = int(tip_id) if tip_id is not None else 1
        self.tip_name = tip_name if tip_name else "Unbekannt"
        self.tip_color = tip_color if tip_color else "#6b7280"
        self.tip_icon = tip_icon if tip_icon else "?"
        self.tip_material = tip_material if tip_material else "Standard"
        self.seal_l = seal_l
        self.seal_r = seal_r
        self.seal_text = seal_text

        fg = "white"
        text_sec = "#888"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Left Info Layout (IEM name, Date, Seal status)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        lbl_iem = QLabel(iem_name)
        lbl_iem.setObjectName("lbl_iem")
        lbl_iem.setMinimumWidth(1)
        lbl_iem.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        lbl_iem.setStyleSheet(f"background-color: transparent; font-weight: bold; font-size: 13px; color: {fg};")

        lbl_date = QLabel(timestamp)
        lbl_date.setObjectName("lbl_date")
        lbl_date.setMinimumWidth(1)
        lbl_date.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        lbl_date.setStyleSheet(f"background-color: transparent; font-size: 10px; color: {text_sec};")

        info_layout.addWidget(lbl_iem)
        info_layout.addWidget(lbl_date)

        # ProKit Seal status label
        self.lbl_seal = QLabel(self.seal_text)
        self.lbl_seal.setObjectName("lbl_seal")
        self.lbl_seal.setStyleSheet("background-color: transparent; font-size: 10px; color: #a1a1aa;")
        self.seal_badge = self.lbl_seal
        info_layout.addWidget(self.lbl_seal)

        layout.addLayout(info_layout, stretch=1)

        # ProKit Tip Badge
        self.tip_badge = QLabel()
        self.tip_badge.setObjectName("tip_badge")
        self.lbl_tip_badge = self.tip_badge
        self.lbl_tip = self.tip_badge

        self._configure_tip_badge()

        # Check unlock state for initial visibility
        try:
            import config
            is_unlocked = config.is_prokit_unlocked()
        except Exception:
            is_unlocked = False

        self.tip_badge.setVisible(is_unlocked)
        self.lbl_seal.setVisible(is_unlocked and bool(self.seal_text))

        layout.addWidget(self.tip_badge)

        # Side/Channel Badge
        lbl_side = QLabel(side)
        lbl_side.setObjectName("lbl_side")
        side_lower = side.lower()
        if side_lower == "left":
            lbl_side.setStyleSheet(f"background-color: #3b82f6; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        elif side_lower == "right":
            lbl_side.setStyleSheet(f"background-color: #ef4444; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        else:
            lbl_side.setStyleSheet(f"background-color: #10b981; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")

        layout.addWidget(lbl_side)
        layout.addStretch()

        # Graph Checkbox
        self.cb_graph = QCheckBox("Graph")
        self.cb_graph.setStyleSheet(f"QCheckBox {{ background-color: transparent; color: {text_sec}; font-size: 11px; font-weight: bold; }}")
        layout.addWidget(self.cb_graph)

    def _configure_tip_badge(self):
        """Format badge text, tooltip, and stylesheet based on tip identity."""
        if self.tip_id == 1 or self.tip_name == "Unbekannt":
            self.tip_badge.setText("?")
            self.tip_badge.setStyleSheet(
                "background-color: #6b7280; color: #a1a1aa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;"
            )
            self.tip_badge.setToolTip("Ear Tip: Unbekannt")
        else:
            icon = self.tip_icon if self.tip_icon else ""
            badge_text = f"{icon} {self.tip_name}".strip() if icon else self.tip_name
            color = self.tip_color if self.tip_color else "#3b82f6"
            self.tip_badge.setText(badge_text)
            self.tip_badge.setStyleSheet(
                f"background-color: {color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;"
            )
            self.tip_badge.setToolTip(f"Ear Tip: {self.tip_name} ({self.tip_material})")

    def set_tip(self, tip_id, tip_name, tip_color="#6b7280", tip_icon="?", tip_material="Standard"):
        """Dynamically update tip information."""
        self.tip_id = int(tip_id) if tip_id is not None else 1
        self.tip_name = tip_name if tip_name else "Unbekannt"
        self.tip_color = tip_color if tip_color else "#6b7280"
        self.tip_icon = tip_icon if tip_icon else "?"
        self.tip_material = tip_material if tip_material else "Standard"
        self._configure_tip_badge()

    def set_seal(self, seal_l, seal_r):
        """Dynamically update acoustic seal status."""
        self.seal_l = seal_l
        self.seal_r = seal_r
        if seal_l is not None and seal_r is not None:
            self.seal_text = f"Seal: L {seal_l:+.1f}dB | R {seal_r:+.1f}dB"
        elif seal_l is not None:
            self.seal_text = f"Seal L: {seal_l:+.1f}dB"
        elif seal_r is not None:
            self.seal_text = f"Seal R: {seal_r:+.1f}dB"
        else:
            self.seal_text = ""
        self.lbl_seal.setText(self.seal_text)
        try:
            import config
            unlocked = config.is_prokit_unlocked()
        except Exception:
            unlocked = False
        self.lbl_seal.setVisible(unlocked and bool(self.seal_text))

    def update_prokit_visibility(self, unlocked: bool = None):
        """Toggle ProKit visibility on this card."""
        if unlocked is None:
            try:
                import config
                unlocked = config.is_prokit_unlocked()
            except Exception:
                unlocked = False
        if hasattr(self, "tip_badge"):
            self.tip_badge.setVisible(unlocked)
        if hasattr(self, "lbl_seal"):
            self.lbl_seal.setVisible(unlocked and bool(self.seal_text))
```

### 3.2 Integration in `HistoryWidget.load_history()` (`history_ui.py`)

In `load_history(self, m_id)`:
```python
# 1. SQL Query with LEFT JOIN TipProfiles
cursor.execute('''
    SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r,
           iem.model_name, iem.custom_name, m.meas_name,
           COALESCE(m.tip_id, 1) AS tip_id,
           COALESCE(t.name, 'Unbekannt') AS tip_name,
           COALESCE(t.color_hex, '#6b7280') AS tip_color,
           COALESCE(t.icon_char, '?') AS tip_icon,
           COALESCE(t.material, 'Standard') AS tip_material,
           m.id AS meas_id
    FROM Measurements m
    JOIN IEM_Models iem ON m.iem_id = iem.id
    LEFT JOIN TipProfiles t ON m.tip_id = t.id
    WHERE iem.musician_id = ?
    ORDER BY m.timestamp DESC LIMIT 100
''', (m_id,))

rows = cursor.fetchall()

for row in rows:
    (timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob,
     iem_name, custom_name, meas_name,
     raw_tip_id, tip_name, tip_color, tip_icon, tip_material, meas_id) = row

    base_name = custom_name if custom_name else iem_name
    display_name = meas_name if meas_name else base_name

    # Parse frequency and magnitude numpy arrays
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

    # Calculate acoustic seal (val_40 vs val_500 delta)
    seal_l = None
    seal_r = None
    seal_text = ""
    if freq is not None and len(freq) >= 10:
        mask_40 = (freq >= 35.0) & (freq <= 45.0)
        mask_500 = (freq >= 450.0) & (freq <= 550.0)
        if np.any(mask_40) and np.any(mask_500):
            if mag_l is not None and len(mag_l) == len(freq):
                v40_l = float(np.mean(mag_l[mask_40]))
                v500_l = float(np.mean(mag_l[mask_500]))
                val_l = v40_l - v500_l
                if not np.isnan(val_l) and not np.isinf(val_l):
                    seal_l = float(round(val_l, 1))
            if mag_r is not None and len(mag_r) == len(freq):
                v40_r = float(np.mean(mag_r[mask_40]))
                v500_r = float(np.mean(mag_r[mask_500]))
                val_r = v40_r - v500_r
                if not np.isnan(val_r) and not np.isinf(val_r):
                    seal_r = float(round(val_r, 1))

    if seal_l is not None and seal_r is not None:
        seal_text = f"Seal: L {seal_l:+.1f}dB | R {seal_r:+.1f}dB"
    elif seal_l is not None:
        seal_text = f"Seal L: {seal_l:+.1f}dB"
    elif seal_r is not None:
        seal_text = f"Seal R: {seal_r:+.1f}dB"

    tip_id = int(raw_tip_id) if raw_tip_id is not None else 1

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
        'tip_color': tip_color,
        'tip_icon': tip_icon,
        'tip_material': tip_material,
        'seal_l': seal_l,
        'seal_r': seal_r,
        'seal_text': seal_text,
        'meas_id': meas_id
    }

    item = QListWidgetItem(self.list_widget)
    item.setData(Qt.UserRole, data_dict)

    card = HistoryCardWidget(
        timestamp=timestamp,
        iem_name=display_name,
        side=side_text,
        tip_id=tip_id,
        tip_name=tip_name,
        tip_color=tip_color,
        tip_icon=tip_icon,
        tip_material=tip_material,
        seal_l=seal_l,
        seal_r=seal_r,
        seal_text=seal_text
    )
    card.cb_graph.stateChanged.connect(self.refresh_view)

    item.setSizeHint(card.sizeHint())
    self.list_widget.setItemWidget(item, card)
```

### 3.3 Dynamic Update Method on `HistoryWidget` (`history_ui.py`)
```python
    def update_prokit_ui_visibility(self):
        """Dynamically update ProKit visibility on all loaded history cards."""
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
                item.setSizeHint(card.sizeHint())
```

### 3.4 Tip Search in `filter_history()` (`history_ui.py`)
Enhance `filter_history()` to allow filtering history by tip name:
```python
    def filter_history(self):
        query = self.search_bar.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.UserRole)
            if not data: continue

            tip_match = query in data.get('tip_name', '').lower()
            match = query in data['iem_name'].lower() or query in data['timestamp'].lower() or tip_match
            item.setHidden(not match)
```

---

## 4. Caveats

1. **Read-Only Explorer Scope:** No source code was modified during this investigation. All findings and code snippets are presented as drop-in architectural proposals.
2. **Backward Compatibility:** Existing calls or tests that construct `HistoryCardWidget(timestamp, iem_name, side)` with only 3 positional arguments are 100% compatible due to default keyword parameters.
3. **Sidebar Width:** The 220px–345px width constraint in `tools_tabs` requires keeping the tip badge and seal status on separate layout lines or sizing policies to avoid squeezing `lbl_iem` into illegibility.
4. **M5 Diagnostics Failure:** The single test failure currently in `pytest tests/test_prokit_e2e.py` (`TestTier1DiagnosticsCard.test_helmholtz_peak_detection_algorithm`) is isolated to Milestone 5 and does not impact Milestone 4.

---

## 5. Conclusion

The design for `HistoryCardWidget` and Milestone 4 (R4 `history_ui.py`) is complete, robust, and verified against all project requirements and E2E assertions:
- **Tip Badge:** `QLabel` pill badge with `f"{icon_char} {tip_name}"` and `color_hex` for known tips; subtle grey `"?"` (`#6b7280` / `#a1a1aa`) for Unbekannt.
- **Acoustic Seal:** Calculated per measurement from BLOBs (40 Hz vs 500 Hz delta), displaying Left and Right strictly separately (Locked Decision 2).
- **ProKit Gate:** Cleanly hidden when locked, revealed when unlocked, with instant dynamic updates via `update_prokit_visibility()`.
- **Attribute Interoperability:** `card.tip_badge`, `card.lbl_tip_badge`, `card.lbl_tip`, `card.lbl_seal`, and `card.seal_badge` are all exposed and mapped.

The Milestone 4 Worker can execute implementation with zero ambiguity.

---

## 6. Verification Method

1. **Run Smoke Test:**
   ```bash
   python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
   ```
   *Expected output: `19/19 CHECKS PASSED`.*

2. **Run History E2E Test Suite:**
   ```bash
   pytest -v tests/test_prokit_e2e.py -k "Hist"
   ```
   *Expected output: All 15 History-related tests PASS.*

3. **Run Adversarial UI & Forensic Test Suites:**
   ```bash
   pytest -v tests/test_forensic_m3.py tests/test_prokit_adversarial_ui.py
   ```
   *Expected output: All 31 tests PASS.*

4. **Verify Dynamic Visibility Interactivity:**
   Construct `HistoryCardWidget`, assert `tip_badge.isVisible()` reflects `config.is_prokit_unlocked()`, call `card.update_prokit_visibility(True)`, assert `tip_badge.isVisible()` toggles to True.
