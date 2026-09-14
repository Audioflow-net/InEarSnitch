import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Add the button
pattern_btn = r'''        self\.btn_export_history = QPushButton\("Export Selected"\)'''
replacement_btn = r'''        self.btn_save_target = QPushButton("Save as Target")
        self.btn_save_target.setToolTip("Saves the selected measurement to the Reference Targets folder (Squiglink targets)")
        self.btn_save_target.setStyleSheet(btn_style)
        self.btn_save_target.clicked.connect(self.save_as_target)
        btn_row.addWidget(self.btn_save_target)
        
        self.btn_export_history = QPushButton("Export Selected")'''
code = re.sub(pattern_btn, replacement_btn, code)

# 2. Add the method
injection_method = r'''    def save_as_target(self):
        import __main__
        from PyQt5.QtWidgets import QMessageBox, QInputDialog
        import numpy as np
        import os
        
        checked_rows = self.get_checked_rows()
        if not checked_rows:
            QMessageBox.warning(self, "Save as Target", "Please check exactly ONE measurement (in the Graph column) to save as a Target.")
            return
            
        if len(checked_rows) > 1:
            QMessageBox.warning(self, "Save as Target", "Please select only ONE measurement to save as a Target.")
            return
            
        row_idx = checked_rows[0]
        data = self.measurements[row_idx]
        freqs = data['freq']
        mag_l = data['mag_l']
        
        if freqs is None or mag_l is None:
            QMessageBox.critical(self, "Error", "Measurement is missing frequency or magnitude data.")
            return
            
        # Default name
        default_name = self.table.item(row_idx, 1).text() # IEM name
        notes = self.table.item(row_idx, 3).text()
        if notes:
            default_name = f"{default_name} ({notes})"
            
        target_name, ok = QInputDialog.getText(self, "Save as Target", "Enter a name for this Target Curve:", text=default_name)
        if not ok or not target_name.strip():
            return
            
        target_name = target_name.strip()
        
        # Save to reference_targets/Pro_Live_IEMs
        target_dir = os.path.join("reference_targets", "Pro_Live_IEMs")
        os.makedirs(target_dir, exist_ok=True)
        
        safe_name = "".join([c if c.isalnum() or c in " -_()" else "_" for c in target_name])
        filepath = os.path.join(target_dir, f"{safe_name}.csv")
        
        try:
            # We must save Freq, Mag_L
            out_array = np.column_stack([freqs, mag_l])
            np.savetxt(filepath, out_array, delimiter=',', header="Frequency,Mag_L", comments='', fmt='%.2f')
            QMessageBox.information(self, "Success", f"Saved as Target: {safe_name}\nIt will now appear in the Target dropdowns.")
            
            # Reload dropdowns
            if hasattr(__main__, 'window') and hasattr(__main__.window, 'load_targets'):
                __main__.window.load_targets()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save Target: {e}")

    def export_selected_csv(self):'''

code = code.replace('    def export_selected_csv(self):', injection_method)

with open("history_ui.py", "w") as f:
    f.write(code)

print("Save as Target patched.")
