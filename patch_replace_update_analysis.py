import re

with open("main.py", "r") as f:
    code = f.read()

old_code = """        self.page_ana.update_analysis(
            self.temp_freqs, self.temp_mag_l, self.temp_mag_r,
            ref_l, ref_r, tgt_f, tgt_m, thd_data=thd_data, csd_data=csd_data
        )"""

new_code = """        self.temp_thd_data = thd_data
        self.temp_csd_data = csd_data
        self.update_analysis_view()"""

code = code.replace(old_code, new_code)

with open("main.py", "w") as f:
    f.write(code)

print("update_analysis call replaced.")
