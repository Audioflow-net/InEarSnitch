import re

with open("main.py", "r") as f:
    code = f.read()

old_import = "from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QSize"
new_import = "from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QSize, QEvent"
code = code.replace(old_import, new_import)

with open("main.py", "w") as f:
    f.write(code)
print("QEvent imported.")
