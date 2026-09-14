import re

with open("main.py", "r") as f:
    code = f.read()

# Remove cb_target from setup_ui
pattern_cb_target = re.compile(r'        control_layout\.addWidget\(QLabel\("Overlay:".*?self\.chk_target = type\(\'Dummy\', \(object,\), \{\'isChecked\': lambda self: True\}\)\(\)\n        \n', re.DOTALL)
code = re.sub(pattern_cb_target, '', code)

with open("main.py", "w") as f:
    f.write(code)

print("cb_target removed from layout.")
