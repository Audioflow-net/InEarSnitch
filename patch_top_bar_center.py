import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''        top_layout\.addWidget\(logo\)
        top_layout\.addWidget\(sublogo\)
        top_layout\.addStretch\(\)

        # Global Status
        self\.lbl_active_profile = QLabel\("No Profile Selected"\)
        self\.lbl_active_profile\.setStyleSheet\("color: #00FF99; font-size: 13px; font-weight: bold; margin-right: 15px;"\)
        top_layout\.addWidget\(self\.lbl_active_profile\)'''

replacement = '''        top_layout.addWidget(logo)
        top_layout.addWidget(sublogo)
        
        # Center the profile label
        top_layout.addStretch()
        
        # Global Status
        self.lbl_active_profile = QLabel("No Profile Selected")
        self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold;")
        top_layout.addWidget(self.lbl_active_profile)
        
        top_layout.addStretch()'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Top bar label centered.")
