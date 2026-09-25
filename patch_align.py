import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# THD
content = content.replace("thd_top_bar = QHBoxLayout()\n        thd_top_bar.addWidget(self.thd_help_lbl)\n        thd_top_bar.addStretch()\n        thd_top_bar.addWidget(btn_thd_help)", "thd_top_bar = QHBoxLayout()\n        thd_top_bar.addStretch()\n        thd_top_bar.addWidget(self.thd_help_lbl)\n        thd_top_bar.addWidget(btn_thd_help)")

# CSD
content = content.replace("csd_top_bar = QHBoxLayout()\n        csd_top_bar.addWidget(self.csd_help_lbl)\n        csd_top_bar.addStretch()\n        csd_top_bar.addWidget(btn_csd_help)", "csd_top_bar = QHBoxLayout()\n        csd_top_bar.addStretch()\n        csd_top_bar.addWidget(self.csd_help_lbl)\n        csd_top_bar.addWidget(btn_csd_help)")

with open("analysis_ui.py", "w") as f:
    f.write(content)
