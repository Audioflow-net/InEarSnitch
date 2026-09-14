with open('theme.py', 'r') as f:
    content = f.read()

content = content.replace('QMessageBox {', 'QMessageBox {{')
content = content.replace('QMessageBox QLabel {', 'QMessageBox QLabel {{')
content = content.replace('QMessageBox QPushButton {', 'QMessageBox QPushButton {{')
content = content.replace('QMessageBox QPushButton:hover {', 'QMessageBox QPushButton:hover {{')

# Fix closing braces for those blocks. We can regex match the closing braces.
import re
content = re.sub(r'(\n\s*color: \{get_color\([^\}]+\)\};\n\s*)\}', r'\1}}', content)
content = re.sub(r'(\n\s*background-color: transparent;\n\s*)\}', r'\1}}', content)
content = re.sub(r'(\n\s*border-radius: 4px;\n\s*)\}', r'\1}}', content)
content = re.sub(r'(\n\s*border: 1px solid \{get_color\([^}]+\)\};\n\s*)\}', r'\1}}', content)

with open('theme.py', 'w') as f:
    f.write(content)
print("SUCCESS")
