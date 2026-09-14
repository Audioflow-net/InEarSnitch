import re

with open('main.py', 'r') as f:
    content = f.read()

old_code = r"""    def clear_trace\(self\):
        self\.plot_widget\.clear\(\)
        self\.temp_freqs = None
        self\.temp_mag_l = None
        self\.temp_mag_r = None
        self\.temp_phase_l = None
        self\.temp_phase_r = None
        self\.temp_ir_l = None
        self\.temp_ir_r = None
        self\.ref_freqs = None
        self\.ref_mag_l = None
        self\.ref_mag_r = None
        self\.plot_target_curve\(\)
        self\.sub_lbl\.setText\("Trace cleared\."\)
        self\.sub_lbl\.setStyleSheet\("color: #888; font-size: 12px;"\)"""

new_code = """    def clear_trace(self):
        self.plot_widget.clear()
        self.temp_freqs = None
        self.temp_mag_l = None
        self.temp_mag_r = None
        self.temp_phase_l = None
        self.temp_phase_r = None
        self.temp_ir_l = None
        self.temp_ir_r = None
        self.ref_freqs = None
        self.ref_mag_l = None
        self.ref_mag_r = None
        self.plot_target_curve()
        self.update_analysis_view()  # <-- PRO UPDATE: Force analysis tab to redraw (clear itself)
        self.sub_lbl.setText("Trace cleared.")
        self.sub_lbl.setStyleSheet("color: #888; font-size: 12px;")"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    with open('main.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
