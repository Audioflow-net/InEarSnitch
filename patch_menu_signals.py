import re

with open("profile_ui.py", "r") as f:
    content = f.read()

# Fix context menu signals in ProfilePicWidget
content = content.replace("action_upload.triggered.connect(self.clicked.emit)", "action_upload.triggered.connect(lambda *args: self.clicked.emit())")
content = content.replace("action_color.triggered.connect(self.color_clicked.emit)", "action_color.triggered.connect(lambda *args: self.color_clicked.emit())")
content = content.replace("action_delete.triggered.connect(self.delete_clicked.emit)", "action_delete.triggered.connect(lambda *args: self.delete_clicked.emit())")

with open("profile_ui.py", "w") as f:
    f.write(content)
