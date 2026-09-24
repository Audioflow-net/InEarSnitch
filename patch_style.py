import sys

with open("main.py", "r") as f:
    content = f.read()

# 1. Patch AvatarButton update_style
old_avatar = """    def update_style(self, selected):
        import theme
        
        if getattr(self, 'is_selected_state', None) == selected:
            return
        self.is_selected_state = selected
        
        if selected:
            bg = "transparent" if self.has_pic else ("#0284c7" if theme.CURRENT_MODE == "light" else "#00FFFF")
            text_col = "#ffffff" if theme.CURRENT_MODE == "light" else "#000000"
            border_col = "#0284c7" if theme.CURRENT_MODE == "light" else "#00FFFF"
            self.setStyleSheet(f"QLabel {{ background-color: {bg}; color: {text_col}; border: 2px solid {border_col}; border-radius: 18px; font-weight: bold; font-size: 14px; outline: none; }}")
        else:
            bg = "transparent" if self.has_pic else self.color
            text_col = "#ffffff" if self.has_pic else self._get_text_color_for_bg(self.color)
            border_col = "#e4e4e7" if theme.CURRENT_MODE == "light" else "#2d2d34"
            self.setStyleSheet(f"QLabel {{ background-color: {bg}; border: 2px solid {border_col}; border-radius: 18px; color: {text_col}; font-weight: bold; font-size: 14px; outline: none; }}")"""

new_avatar = """    def update_style(self, selected):
        import theme
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        
        if getattr(self, 'is_selected_state', None) == selected:
            return
        self.is_selected_state = selected
        
        if selected:
            bg = "transparent" if self.has_pic else ("#3b82f6" if theme.CURRENT_MODE == "dark" else "#2563eb")
            text_col = "#ffffff"
            border_col = "#60a5fa" if theme.CURRENT_MODE == "dark" else "#3b82f6"
            self.setStyleSheet(f"QLabel {{ background-color: {bg}; color: {text_col}; border: 2px solid {border_col}; border-radius: 18px; font-weight: bold; font-size: 14px; outline: none; }}")
            
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 0)
            if theme.CURRENT_MODE == "light":
                shadow.setColor(QColor(37, 99, 235, 120))
            else:
                shadow.setColor(QColor(96, 165, 250, 180))
            self.setGraphicsEffect(shadow)
        else:
            bg = "transparent" if self.has_pic else self.color
            text_col = "#ffffff" if self.has_pic else self._get_text_color_for_bg(self.color)
            border_col = "#e4e4e7" if theme.CURRENT_MODE == "light" else "#3f3f46"
            self.setStyleSheet(f"QLabel {{ background-color: {bg}; border: 1px solid {border_col}; border-radius: 18px; color: {text_col}; font-weight: bold; font-size: 14px; outline: none; }}")
            self.setGraphicsEffect(None)"""
content = content.replace(old_avatar, new_avatar, 1)


# 2. Patch MusicianCard force_profile_selection
old_card = """                if is_sel:
                    if theme.CURRENT_MODE == "light":
                        c.setStyleSheet("#musicianCardObj { background-color: #e4e4e7; border-radius: 8px; border: 2px solid #0284c7; outline: none; }")
                    else:
                        c.setStyleSheet("#musicianCardObj { background-color: #3f3f46; border-radius: 8px; border: 2px solid #00FFFF; outline: none; }")
                else:
                    if theme.CURRENT_MODE == "light":
                        c.setStyleSheet("#musicianCardObj { background-color: #ffffff; border-radius: 8px; border: none; outline: none; }")
                    else:
                        c.setStyleSheet("#musicianCardObj { background-color: #2d2d34; border-radius: 8px; border: none; outline: none; }")
                
                if is_sel:
                    shadow = QGraphicsDropShadowEffect(c)
                    if theme.CURRENT_MODE == "light":
                        shadow.setBlurRadius(20)
                        shadow.setColor(QColor(0, 0, 0, 70))
                        shadow.setOffset(0, 6)
                    else:

                        # Subtle cyan glow in dark mode for elegant 3D lift
                        shadow.setBlurRadius(30)
                        shadow.setColor(QColor(0, 255, 255, 40))
                        shadow.setOffset(0, 0)
                    c.setGraphicsEffect(shadow)
                else:
                    c.setGraphicsEffect(None)"""

new_card = """                if is_sel:
                    if theme.CURRENT_MODE == "light":
                        c.setStyleSheet("#musicianCardObj { background-color: #f4f4f5; border-radius: 8px; border: 1px solid #e4e4e7; border-left: 4px solid #3b82f6; outline: none; }")
                    else:
                        c.setStyleSheet("#musicianCardObj { background-color: #3f3f46; border-radius: 8px; border: 1px solid #52525b; border-left: 4px solid #3b82f6; outline: none; }")
                else:
                    if theme.CURRENT_MODE == "light":
                        c.setStyleSheet("#musicianCardObj { background-color: #ffffff; border-radius: 8px; border: 1px solid transparent; outline: none; }")
                    else:
                        c.setStyleSheet("#musicianCardObj { background-color: #2d2d34; border-radius: 8px; border: 1px solid transparent; outline: none; }")
                
                if is_sel:
                    shadow = QGraphicsDropShadowEffect(c)
                    if theme.CURRENT_MODE == "light":
                        shadow.setBlurRadius(20)
                        shadow.setColor(QColor(0, 0, 0, 70))
                        shadow.setOffset(0, 6)
                    else:
                        # Subtle modern blue glow in dark mode
                        shadow.setBlurRadius(30)
                        shadow.setColor(QColor(59, 130, 246, 40))
                        shadow.setOffset(0, 0)
                    c.setGraphicsEffect(shadow)
                else:
                    c.setGraphicsEffect(None)"""
content = content.replace(old_card, new_card, 1)

with open("main.py", "w") as f:
    f.write(content)
print("done")
