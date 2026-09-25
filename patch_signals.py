import re

with open("profile_ui.py", "r") as f:
    content = f.read()

# Replace direct emits with lambda _: emit()
content = content.replace("connect(self.data_changed.emit)", "connect(lambda *args: self.data_changed.emit())")

with open("profile_ui.py", "w") as f:
    f.write(content)
