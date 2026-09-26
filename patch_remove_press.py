import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """        # When clicking into the text area, clear text and show popup
        self.lineEdit().mousePressEvent = self._handle_mouse_press
        
    def _handle_mouse_press(self, event):
        super(QComboBox, self).lineEdit().mousePressEvent(event)
        self.lineEdit().clear()
        self.showPopup()"""

new_logic = """        # Event handling is done via eventFilter in load_targets"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)

with open("analysis_ui.py", "r") as f:
    ana_content = f.read()

old_ana_logic = """        self.lineEdit().mousePressEvent = self._handle_mouse_press
        
    def _handle_mouse_press(self, event):
        super(QComboBox, self).lineEdit().mousePressEvent(event)
        self.lineEdit().clear()
        self.showPopup()"""

new_ana_logic = """        pass"""

ana_content = ana_content.replace(old_ana_logic, new_ana_logic)

with open("analysis_ui.py", "w") as f:
    f.write(ana_content)
