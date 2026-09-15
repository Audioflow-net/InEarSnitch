import re

with open("history_ui.py", "r") as f:
    content = f.read()

save_notes_rep = """    def save_notes(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        old_ts = data['timestamp']
        
        new_notes = self.txt_notes.toPlainText()
        new_name = self.edit_meas_name.text().strip()
        new_ts = self.edit_meas_date.text().strip()
        
        # fallback if empty
        if not new_ts: new_ts = old_ts
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # If timestamp changed, check if new one exists to prevent collision
            if new_ts != old_ts:
                cursor.execute("SELECT 1 FROM Measurements WHERE timestamp = ?", (new_ts,))
                if cursor.fetchone():
                    # Collision! Revert UI to old timestamp
                    self.edit_meas_date.blockSignals(True)
                    self.edit_meas_date.setText(old_ts)
                    self.edit_meas_date.blockSignals(False)
                    new_ts = old_ts
            
            cursor.execute('UPDATE Measurements SET notes = ?, meas_name = ?, timestamp = ? WHERE timestamp = ?', 
                           (new_notes, new_name, new_ts, old_ts))
            conn.commit()
            conn.close()
            
            # Update item data
            data['notes'] = new_notes
            data['meas_name'] = new_name
            data['timestamp'] = new_ts
            data['iem_name'] = new_name if new_name else data.get('base_name', '')
            items[0].setData(Qt.UserRole, data)
            
            # Update Card UI
            from PySide6.QtWidgets import QLabel
            card = self.list_widget.itemWidget(items[0])
            if card:
                lbl_iem = card.findChild(QLabel, "lbl_iem")
                lbl_date = card.findChild(QLabel, "lbl_date")
                if lbl_iem: lbl_iem.setText(data['iem_name'])
                if lbl_date: lbl_date.setText(data['timestamp'])
                
        except Exception as e:
            print(f"Error autosaving: {e}")"""

# Find the save_notes function and replace it until the next def
import re
content = re.sub(r"    def save_notes\(self\):.*?(?=    def \w+\(self)", save_notes_rep + "\n\n", content, flags=re.DOTALL)

with open("history_ui.py", "w") as f:
    f.write(content)
