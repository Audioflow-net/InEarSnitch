with open('analysis_ui.py', 'r') as f:
    content = f.read()

import re
content = re.sub(
    r'self\.btn_stress_test\.setStyleSheet\([^)]+\)',
    'self.btn_stress_test.setProperty("class", "danger")',
    content
)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
