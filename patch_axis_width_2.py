import re

with open("analysis_ui.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "self.plot_widget.setLabel('left', 'Magnitude', units='dB')" in line:
        lines[i] = line + "        self.plot_widget.getAxis('left').setWidth(45)\n"
    elif "self.thd_widget.setLabel('left', 'THD', units='%')" in line:
        lines[i] = line + "        self.thd_widget.getAxis('left').setWidth(45)\n"
    elif "self.csd_widget.setLabel('left', 'Magnitude (dB)')" in line:
        lines[i] = line + "        self.csd_widget.getAxis('left').setWidth(45)\n"

with open("analysis_ui.py", "w") as f:
    f.writelines(lines)
