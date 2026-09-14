import re

with open('history_ui.py', 'r') as f:
    content = f.read()

content = content.replace("QPushButton, QWidget, ", "QPushButton, QWidget, QTabWidget, ")

with open('history_ui.py', 'w') as f:
    f.write(content)
