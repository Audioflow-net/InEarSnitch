import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Remove event filter logic from __init__
code = code.replace("QApplication.instance().installEventFilter(self)", "")

# 2. Remove eventFilter method
import ast
# We'll use regex to strip out def eventFilter(self, obj, event): ... return super().eventFilter(obj, event)
pattern = re.compile(r'    def eventFilter\(self, obj, event\):.*?return super\(\)\.eventFilter\(obj, event\)\n', re.DOTALL)
code = re.sub(pattern, '', code)

# 3. Add dimmer button in setup_ui
old_settings_panel = """        # --- Settings Overlay Panel ---
        page_set = QFrame(self)"""

new_settings_panel = """        # --- Settings Overlay Panel ---
        from PyQt5.QtWidgets import QPushButton
        self.settings_dimmer = QPushButton(self)
        self.settings_dimmer.setStyleSheet("background: transparent; border: none;")
        self.settings_dimmer.hide()
        # when clicked, hide panel and itself
        self.settings_dimmer.clicked.connect(lambda: self.settings_panel.setVisible(False) or self.settings_dimmer.setVisible(False))
        
        page_set = QFrame(self)"""
code = code.replace(old_settings_panel, new_settings_panel)

# 4. Update _toggle_settings
old_toggle = """        def _toggle_settings():
            is_visible = self.settings_panel.isVisible()
            self.settings_panel.setVisible(not is_visible)
            if not is_visible:"""

new_toggle = """        def _toggle_settings():
            is_visible = self.settings_panel.isVisible()
            self.settings_panel.setVisible(not is_visible)
            if hasattr(self, 'settings_dimmer'):
                self.settings_dimmer.setVisible(not is_visible)
                if not is_visible:
                    self.settings_dimmer.raise_()
                    self.settings_panel.raise_()
            if not is_visible:"""
code = code.replace(old_toggle, new_toggle)

# 5. Update resizeEvent
old_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'settings_panel') and self.settings_panel is not None:"""

new_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'settings_dimmer'):
            self.settings_dimmer.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, 'settings_panel') and self.settings_panel is not None:"""
code = code.replace(old_resize, new_resize)

# 6. Update _save_settings to hide dimmer
old_save = """        # Close panel after saving
        self.settings_panel.setVisible(False)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")"""

new_save = """        # Close panel after saving
        self.settings_panel.setVisible(False)
        if hasattr(self, 'settings_dimmer'): self.settings_dimmer.setVisible(False)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")"""
code = code.replace(old_save, new_save)

with open("main.py", "w") as f:
    f.write(code)
print("Dimmer overlay patched.")
