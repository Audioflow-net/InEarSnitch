import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# For plot_widget
content = content.replace("self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')", "self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')\n        self.plot_widget.getAxis('bottom').setHeight(25)")

# For thd_widget
content = content.replace("self.thd_widget.setLabel('bottom', 'Frequency', units='Hz')", "self.thd_widget.setLabel('bottom', 'Frequency', units='Hz')\n        self.thd_widget.getAxis('bottom').setHeight(25)")

# For csd_widget
content = content.replace("self.csd_widget.setLabel('bottom', 'Frequency', units='Hz')", "self.csd_widget.setLabel('bottom', 'Frequency', units='Hz')\n        self.csd_widget.getAxis('bottom').setHeight(25)")

with open("analysis_ui.py", "w") as f:
    f.write(content)
