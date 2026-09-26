import re

with open("main.py", "r") as f:
    content = f.read()

# Fix QtCore references in main.py
content = content.replace("QtCore.QEvent.MouseButtonPress", "QEvent.MouseButtonPress")
content = content.replace("QtCore.QEvent.FocusOut", "QEvent.FocusOut")
content = content.replace("QtCore.QTimer.singleShot", "QTimer.singleShot")

with open("main.py", "w") as f:
    f.write(content)
