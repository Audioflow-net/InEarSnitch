import re

with open("history_ui.py", "r") as f:
    code = f.read()

# Replace on_item_changed and on_item_selected and refresh_view and load_history and filter_history
# Actually, I'll just find where load_history starts and replace the rest of the file (or a huge chunk).
# Let's inspect where load_history starts:

# It starts at "def load_history(self, m_id):"
import sys

idx = code.find("def load_history")
if idx == -1:
    print("Could not find load_history")
    sys.exit(1)
    
new_logic = """def load_history(self, m_id):
        self.last_m_id = m_id
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self.measurements = []
        self.plot_widget.clear()
        self.edit_container.setEnabled(False)
        self.txt_notes.clear()
        
        if not os.path.exists(self.db_path):
            print(f"Database {self.db_path} not found.")
            return

        try:
            import sqlite3
            import numpy as np
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name
                FROM Measurements m
                JOIN IEM_Models iem ON m.iem_id = iem.id
                WHERE iem.musician_id = ?
                ORDER BY m.timestamp DESC LIMIT 100
            ''', (m_id,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob, iem_name, custom_name = row
                display_name = custom_name if custom_name else iem_name
                
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
                    'side': side_text
                }
                
                item = QListWidgetItem(self.list_widget)
                item.setData(Qt.UserRole, data_dict)
                
                card = HistoryCardWidget(timestamp, display_name, side_text)
                card.cb_graph.stateChanged.connect(self.refresh_view)
                
                # Ensure the item is big enough for the card
                item.setSizeHint(card.sizeHint())
                self.list_widget.setItemWidget(item, card)
                
            conn.close()
            
        except Exception as e:
            print(f"Error loading history: {e}")
        
        self.list_widget.blockSignals(False)
        self.refresh_view()
        self.filter_history()

    def filter_history(self):
        query = self.search_bar.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.UserRole)
            if not data: continue
            
            match = query in data['iem_name'].lower() or query in data['timestamp'].lower()
            item.setHidden(not match)

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        if not items:
            self.edit_container.setEnabled(False)
            self.txt_notes.clear()
            return
            
        self.edit_container.setEnabled(True)
        data = items[0].data(Qt.UserRole)
        self.txt_notes.blockSignals(True)
        self.txt_notes.setText(data.get('notes', ''))
        self.txt_notes.blockSignals(False)

    def save_notes(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        ts = data['timestamp']
        new_notes = self.txt_notes.text()
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE Measurements SET notes = ? WHERE timestamp = ?', (new_notes, ts))
            conn.commit()
            conn.close()
            data['notes'] = new_notes
            items[0].setData(Qt.UserRole, data)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def on_item_checked(self):
        self.refresh_view()

    def refresh_view(self):
        self.plot_widget.clear()
        
        import numpy as np
        from audio_engine import AudioEngine
        from theme import theme
        from PySide6.QtCore import Qt
        import pyqtgraph as pg
        
        color_idx = 0
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            card = self.list_widget.itemWidget(item)
            
            if card and card.cb_graph.isChecked():
                data = item.data(Qt.UserRole)
                freq = data['freq']
                mag_l = data['mag_l']
                mag_r = data['mag_r']
                ts = data['timestamp']
                
                if freq is not None:
                    color = self.colors[color_idx % len(self.colors)]
                    
                    show_l = self.btn_chan_l.isChecked()
                    show_r = self.btn_chan_r.isChecked()
                    smooth_txt = self.cb_smooth.currentText()
                    
                    pts = 240
                    if smooth_txt == "Raw": pts = None
                    elif smooth_txt == "1/6 Oct": pts = 60
                    elif smooth_txt == "1/12 Oct": pts = 120
                    elif smooth_txt == "1/24 Oct": pts = 240
                    elif smooth_txt == "1/48 Oct": pts = 480
                    
                    if mag_l is not None and show_l:
                        f_plot, m_plot = freq, mag_l
                        if pts is not None:
                            try:
                                res = AudioEngine.smooth_spectrum(freq, mag_l, points=pts)
                                if len(res) == 3: f_plot, m_plot, _ = res
                                else: f_plot, m_plot = res
                            except Exception: pass
                        
                        self.plot_widget.plot(f_plot, m_plot, pen=pg.mkPen(color=color, width=2), name=f"{ts} (L)")
                        
                    if mag_r is not None and show_r:
                        f_plot, m_plot = freq, mag_r
                        if pts is not None:
                            try:
                                res = AudioEngine.smooth_spectrum(freq, mag_r, points=pts)
                                if len(res) == 3: f_plot, m_plot, _ = res
                                else: f_plot, m_plot = res
                            except Exception: pass
                        
                        self.plot_widget.plot(f_plot, m_plot, pen=pg.mkPen(color=color, width=2, style=Qt.DashLine), name=f"{ts} (R)")
                    
                    color_idx += 1

    def delete_selected(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        ts = data['timestamp']
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Delete Measurement', f"Are you sure you want to delete this measurement?\\n{ts}", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Measurements WHERE timestamp = ?', (ts,))
                conn.commit()
                conn.close()
                self.load_history(self.last_m_id)
            except Exception as e:
                print(f"Error deleting measurement: {e}")

    def export_selected_csv(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        freq = data['freq']
        mag_l = data['mag_l']
        mag_r = data['mag_r']
        
        if freq is None: return
        
        from PySide6.QtWidgets import QFileDialog
        import numpy as np
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write("Frequency,Magnitude_L,Magnitude_R\\n")
                    for i in range(len(freq)):
                        l_val = mag_l[i] if mag_l is not None else ''
                        r_val = mag_r[i] if mag_r is not None else ''
                        f.write(f"{freq[i]},{l_val},{r_val}\\n")
            except Exception as e:
                print(f"Error exporting CSV: {e}")

    def save_as_target(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        freq = data['freq']
        mag_l = data['mag_l']
        mag_r = data['mag_r']
        iem = data['iem_name']
        side = data['side']
        
        if freq is None: return
        
        from PySide6.QtWidgets import QInputDialog
        import os
        
        # Decide which side to save if both are present. For Squiglink format, typically we just save one channel or average.
        mag_to_save = mag_l if mag_l is not None else mag_r
        if mag_l is not None and mag_r is not None:
            # Simple average if both are present? Or just ask the user. We'll default to left.
            mag_to_save = mag_l
            
        target_name, ok = QInputDialog.getText(self, "Save Target", "Target Name:", text=f"{iem} Target")
        if ok and target_name:
            try:
                os.makedirs("Reference Targets", exist_ok=True)
                target_path = os.path.join("Reference Targets", f"{target_name.replace('/', '_')}.csv")
                with open(target_path, 'w') as f:
                    for i in range(len(freq)):
                        f.write(f"{freq[i]:.2f},{mag_to_save[i]:.2f}\\n")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Target Saved", f"Target saved to {target_path}")
            except Exception as e:
                print(f"Error saving target: {e}")
"""

new_code = code[:idx] + new_logic
with open("history_ui.py", "w") as f:
    f.write(new_code)
