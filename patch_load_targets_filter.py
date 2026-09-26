import re

with open("main.py", "r") as f:
    content = f.read()

# Let's ensure the event filter is attached to the popup in load_targets, 
# just in case the completer was recreated.
old_load = """                if completer.popup():
                    completer.popup().setStyleSheet("background-color: #111; color: white; border: 1px solid #333;")
                completer.setMaxVisibleItems(25)"""

new_load = """                if completer.popup():
                    completer.popup().setStyleSheet("background-color: #111; color: white; border: 1px solid #333;")
                    # Re-install event filter just in case the popup was recreated
                    completer.popup().removeEventFilter(b)
                    completer.popup().installEventFilter(b)
                completer.setMaxVisibleItems(25)"""

content = content.replace(old_load, new_load)

with open("main.py", "w") as f:
    f.write(content)

with open("analysis_ui.py", "r") as f:
    content_ana = f.read()
    content_ana = content_ana.replace(old_load, new_load)
with open("analysis_ui.py", "w") as f:
    f.write(content_ana)
