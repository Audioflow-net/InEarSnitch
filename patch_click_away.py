import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Close after save
old_save = """        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")
        self.populate_devices()
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")"""

new_save = """        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")
        self.populate_devices()
        # Close panel after saving
        self.settings_panel.setVisible(False)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")"""
code = code.replace(old_save, new_save)

# 2. Add event filter to MainWindow
old_init = """    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)"""

new_init = """    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        QApplication.instance().installEventFilter(self)"""
code = code.replace(old_init, new_init)

old_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)"""

new_resize = """    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if hasattr(self, 'settings_panel') and self.settings_panel and self.settings_panel.isVisible():
                # Check if click is inside settings panel or the settings toggle button
                from PyQt5.QtGui import QMouseEvent
                from PyQt5.QtCore import QPoint
                
                # event.globalPos() is available for mouse events
                global_pos = event.globalPos()
                
                # Map global position to MainWindow coordinates
                local_pos = self.mapFromGlobal(global_pos)
                
                # Check if it's within the settings panel or the button
                in_panel = self.settings_panel.geometry().contains(local_pos)
                
                # Try to map btn_top_settings to main window coords
                btn_local = self.btn_top_settings.mapTo(self, QPoint(0,0))
                btn_rect = self.btn_top_settings.rect()
                btn_rect.moveTo(btn_local)
                in_btn = btn_rect.contains(local_pos)
                
                # Also prevent closing if it's a click inside a popup/dialog (QMessageBox)
                # If obj is a window and not self, it might be a dialog
                is_dialog = obj.isWindow() and obj != self
                
                if not in_panel and not in_btn and not is_dialog:
                    self.settings_panel.setVisible(False)
                    
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)"""
code = code.replace(old_resize, new_resize)

with open("main.py", "w") as f:
    f.write(code)

print("Click-away patched.")
