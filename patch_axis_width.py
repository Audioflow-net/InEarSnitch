import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# For plot_widget
content = content.replace("self.plot_widget.setLabel('left', 'Magnitude (dB)')", "self.plot_widget.setLabel('left', 'Magnitude (dB)')\n        self.plot_widget.getAxis('left').setWidth(45)")

# For thd_widget
content = content.replace("self.thd_widget.setLabel('left', 'Distortion (%)')", "self.thd_widget.setLabel('left', 'Distortion (%)')\n        self.thd_widget.getAxis('left').setWidth(45)")

# For csd_widget
content = content.replace("self.csd_widget.setLabel('left', 'Magnitude')", "self.csd_widget.setLabel('left', 'Magnitude')\n        self.csd_widget.getAxis('left').setWidth(45)")

with open("analysis_ui.py", "w") as f:
    f.write(content)
