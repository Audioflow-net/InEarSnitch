import re

with open("main.py", "r") as f:
    code = f.read()

old_code = """        self.db.save_measurement(
            self.current_iem_id, 
            self.temp_freqs, 
            self.temp_mag_l, 
            self.temp_mag_r, 
            self.temp_phase_l, 
            self.temp_phase_r,
            gain,
            notes,
            ""
        )
        self.sub_lbl.setText("Status: Saved to Database.")
        self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")"""

new_code = """        try:
            self.db.save_measurement(
                self.current_iem_id, 
                self.temp_freqs, 
                self.temp_mag_l, 
                self.temp_mag_r, 
                self.temp_phase_l, 
                self.temp_phase_r,
                gain,
                notes,
                ""
            )
            self.sub_lbl.setText("Status: Saved to Database.")
            self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")
            
            # Immediately update the history tab so it reflects the new save
            if hasattr(self, 'active_card') and self.active_card:
                if hasattr(self.page_hist, 'load_history'):
                    self.page_hist.load_history(self.active_card.m_id)
        except Exception as e:
            self.sub_lbl.setText(f"Status: ERROR saving - {e}")
            self.sub_lbl.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
            print(f"DB Save Error: {e}")"""

code = code.replace(old_code, new_code)

with open("main.py", "w") as f:
    f.write(code)

print("Save patched.")
