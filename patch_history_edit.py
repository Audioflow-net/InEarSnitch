import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Update setEditTriggers in __init__
pattern_edit = r'''        self\.table\.setSelectionMode\(QAbstractItemView\.SingleSelection\)
        self\.table\.setEditTriggers\(QAbstractItemView\.NoEditTriggers\)'''
replacement_edit = r'''        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.itemChanged.connect(self.on_item_changed)'''
code = re.sub(pattern_edit, replacement_edit, code)

# 2. Update the table loading logic
pattern_load = r'''                # Date
                date_item = QTableWidgetItem\(str\(timestamp\)\)
                self\.table\.setItem\(row_idx, 0, date_item\)
                
                # Notes
                notes_item = QTableWidgetItem\(str\(notes\) if notes else ""\)
                self\.table\.setItem\(row_idx, 1, notes_item\)
                
                # Photo icon
                photo_item = QTableWidgetItem\("Photo" if photo_path else ""\)
                photo_item\.setTextAlignment\(Qt\.AlignCenter\)
                self\.table\.setItem\(row_idx, 2, photo_item\)
                
                # Checkbox for Graph
                checkbox_widget = QWidget\(\)
                checkbox_layout = QHBoxLayout\(checkbox_widget\)
                checkbox_layout\.setContentsMargins\(0, 0, 0, 0\)
                checkbox_layout\.setAlignment\(Qt\.AlignCenter\)
                checkbox = QCheckBox\(\)
                checkbox\.stateChanged\.connect\(self\.on_item_checked\)
                checkbox_layout\.addWidget\(checkbox\)
                self\.table\.setCellWidget\(row_idx, 3, checkbox_widget\)'''

replacement_load = r'''                # 0: Date
                date_item = QTableWidgetItem(str(timestamp))
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 0, date_item)
                
                # 1: IEM
                iem_item = QTableWidgetItem(str(iem_name))
                iem_item.setFlags(iem_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 1, iem_item)
                
                # 2: Side (L/R/Stereo)
                side = "Stereo" if (mag_l is not None and mag_r is not None) else ("L" if mag_l is not None else "R")
                side_item = QTableWidgetItem(side)
                side_item.setFlags(side_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 2, side_item)
                
                # 3: Notes (Custom Name) -> EDITABLE!
                notes_item = QTableWidgetItem(str(notes) if notes else "")
                self.table.setItem(row_idx, 3, notes_item)
                
                # 4: Photo icon
                photo_item = QTableWidgetItem("Photo" if photo_path else "")
                photo_item.setTextAlignment(Qt.AlignCenter)
                photo_item.setFlags(photo_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 4, photo_item)
                
                # 5: Checkbox for Graph
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self.on_item_checked)
                checkbox_layout.addWidget(checkbox)
                self.table.setCellWidget(row_idx, 5, checkbox_widget)'''

code = re.sub(pattern_load, replacement_load, code)

# 3. Add blockSignals to load_history
code = code.replace(
    'self.table.setRowCount(0)',
    'self.table.blockSignals(True)\n        self.table.setRowCount(0)'
)
code = code.replace(
    'conn.close()',
    'conn.close()\n            self.table.blockSignals(False)'
)

# 4. Inject on_item_changed
injection = r'''    def on_item_changed(self, item):
        if item.column() == 3: # Notes
            new_notes = item.text()
            row = item.row()
            if row < len(self.measurements):
                ts = self.measurements[row]['timestamp']
                try:
                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    c.execute("UPDATE Measurements SET notes = ? WHERE timestamp = ?", (new_notes, ts))
                    conn.commit()
                    conn.close()
                    self.measurements[row]['notes'] = new_notes
                    
                    # Also notify the main window to update its dropdowns!
                    import __main__
                    if hasattr(__main__, 'window') and hasattr(__main__.window, 'load_targets'):
                        __main__.window.load_targets()
                except Exception as e:
                    print(f"Error saving notes: {e}")

    def on_item_selected(self):'''

code = code.replace('    def on_item_selected(self):', injection)


with open("history_ui.py", "w") as f:
    f.write(code)

print("History edit patched.")
