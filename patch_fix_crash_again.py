import re

for filename in ["history_ui.py", "profile_ui.py"]:
    with open(filename, "r") as f:
        content = f.read()

    # Remove Qt from the local import
    content = content.replace("from PySide6.QtCore import QObject, QEvent, Qt", "from PySide6.QtCore import QObject, QEvent")

    with open(filename, "w") as f:
        f.write(content)
