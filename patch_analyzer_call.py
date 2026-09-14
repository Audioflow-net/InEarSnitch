import re

with open("main.py", "r") as f:
    code = f.read()

old_logic = """        # Run auto-diagnostics ONLY if both L and R are captured
        if self.temp_mag_l is not None and self.temp_mag_r is not None:
            seal_err, seal_msg = Analyzer.auto_seal_detection(freqs, self.temp_mag_l, self.temp_mag_r)
            bal_err, bal_msg = Analyzer.lr_imbalance_check(freqs, self.temp_mag_l, self.temp_mag_r)
            
            warning_txt = ""
            if seal_err or bal_err:
                warning_txt = f"WARNING: {seal_msg if seal_err else ''} {bal_msg if bal_err else ''}"
                
            if warning_txt:
                self.sub_lbl.setText(warning_txt)
                self.sub_lbl.setStyleSheet("color: #FF8C00; font-size: 13px; font-weight: bold;")
            else:
                self.sub_lbl.setText("Status: Capture Complete (L & R matched!). Ready to save.")
                self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")"""

new_logic = """        # Run auto-diagnostics ONLY if both L and R are captured
        if self.temp_mag_l is not None and self.temp_mag_r is not None:
            report_l = Analyzer.absolute_checks(freqs, self.temp_mag_l, "Left")
            report_r = Analyzer.absolute_checks(freqs, self.temp_mag_r, "Right")
            
            failures = [i['desc'] for i in report_l + report_r if i['status'] in ('FAIL', 'WARN')]
            
            if failures:
                self.sub_lbl.setText(f"WARNING: {failures[0]}")
                self.sub_lbl.setStyleSheet("color: #FF8C00; font-size: 13px; font-weight: bold;")
            else:
                self.sub_lbl.setText("Status: Capture Complete (L & R matched!). Ready to save.")
                self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")"""

code = code.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(code)

print("Analyzer call patched.")
