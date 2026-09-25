import re

with open("main.py", "r") as f:
    content = f.read()

old_init = """    def __init__(self, tab_widget, parent=None):
        super().__init__("?", parent)
        self.tab_widget = tab_widget
        self.setFixedSize(24, 24)
        self.setStyleSheet("QPushButton { border-radius: 12px; background: #3f3f46; color: white; font-weight: bold; font-size: 13px; border: none; } QPushButton:hover { background: #0ea5e9; }")
        self.setCursor(Qt.PointingHandCursor)
        
        self.popup = QLabel(parent, Qt.ToolTip)
        self.popup.setStyleSheet("background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 8px; padding: 12px; font-size: 13px;")
        self.popup.setWordWrap(True)
        self.popup.setMinimumWidth(550)
        self.popup.hide()"""

new_init = """    def __init__(self, tab_widget, parent=None):
        super().__init__("?", parent)
        self.tab_widget = tab_widget
        self.setFixedSize(24, 24)
        self.setCursor(Qt.PointingHandCursor)
        
        self.popup = QLabel(parent, Qt.ToolTip)
        self.popup.setWordWrap(True)
        self.popup.setMinimumWidth(550)
        self.popup.hide()
        self.update_styling()
        
    def update_styling(self):
        import theme
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        accent = theme.get_color('accent')
        btn_bg = theme.get_color('bg_hover')
        
        self.setStyleSheet(f"QPushButton {{ border-radius: 12px; background: {btn_bg}; color: {fg}; font-weight: bold; font-size: 13px; border: 1px solid {border}; }} QPushButton:hover {{ background: {accent}; color: #000000; border: none; }}")
        self.popup.setStyleSheet(f"background-color: {bg}; color: {fg}; border: 1px solid {accent}; border-radius: 8px; padding: 12px; font-size: 13px;")"""

content = content.replace(old_init, new_init)

# Inject update_styling call into on_theme_toggle in main.py
theme_hook_old = """        self.page_ana.btn_capture.update_style()
        self.page_ana.btn_trace.update_style()
        self.page_ana.btn_save_db.update_style()"""

theme_hook_new = """        self.page_ana.btn_capture.update_style()
        self.page_ana.btn_trace.update_style()
        self.page_ana.btn_save_db.update_style()
        if hasattr(self, 'btn_global_help'):
            self.btn_global_help.update_styling()"""
            
content = content.replace(theme_hook_old, theme_hook_new)

with open("main.py", "w") as f:
    f.write(content)
