import re

with open("main.py", "r") as f:
    code = f.read()

# We will just find def resizeEvent and inject the code
old_code = """    def resizeEvent(self, event):
        super().resizeEvent(event)"""

new_code = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'settings_dimmer'):
            self.settings_dimmer.setGeometry(0, 0, self.width(), self.height())"""

code = code.replace(old_code, new_code)

with open("main.py", "w") as f:
    f.write(code)

print("resizeEvent patched.")
