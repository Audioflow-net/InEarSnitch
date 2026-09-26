import re

with open("main.py", "r") as f:
    content = f.read()

old_completer = """            completer = b.completer()
            if completer:
                completer.setCompletionMode(QCompleter.PopupCompletion)
                completer.setFilterMode(Qt.MatchContains)"""

new_completer = """            completer = b.completer()
            if completer:
                completer.setCompletionMode(QCompleter.PopupCompletion)
                completer.setFilterMode(Qt.MatchContains)
                if completer.popup():
                    completer.popup().setStyleSheet("background-color: #111; color: white; border: 1px solid #333;")
                completer.setMaxVisibleItems(25)"""

content = content.replace(old_completer, new_completer)

with open("main.py", "w") as f:
    f.write(content)
