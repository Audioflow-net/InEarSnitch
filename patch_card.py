import re

with open("history_ui.py", "r") as f:
    content = f.read()

# Make labels shrinkable
label_patch = """        lbl_iem = QLabel(iem_name)
        lbl_iem.setObjectName("lbl_iem")
        lbl_iem.setMinimumWidth(1)
        lbl_iem.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        lbl_iem.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {fg};")
        
        lbl_date = QLabel(timestamp)
        lbl_date.setObjectName("lbl_date")
        lbl_date.setMinimumWidth(1)
        lbl_date.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        lbl_date.setStyleSheet(f"font-size: 10px; color: {text_sec};")"""

content = re.sub(r"        lbl_iem = QLabel\(iem_name\).*?lbl_date\.setStyleSheet\(f\"font-size: 10px; color: \{text_sec\};\"\)", label_patch, content, flags=re.DOTALL)

# Add stretch to info_layout
content = content.replace("layout.addLayout(info_layout)\n        layout.addWidget(lbl_side)", "layout.addLayout(info_layout, stretch=1)\n        layout.addWidget(lbl_side)")

with open("history_ui.py", "w") as f:
    f.write(content)
