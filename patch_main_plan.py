import re

with open('main.py', 'r') as f:
    content = f.read()

# Update AvatarButton.update_style
avatar_code = """    def update_style(self, selected):
        self.setProperty("class", "avatar_btn_pic" if self.has_pic else "avatar_btn")
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)
"""
content = re.sub(
    r'    def update_style\(self, selected\):.*?(?=\n    def mousePressEvent|\n$)',
    avatar_code,
    content,
    flags=re.DOTALL
)

# Update MusicianCard initial style setup
content = re.sub(
    r'\s*if theme\.CURRENT_MODE == "light":\n\s*self\.setStyleSheet\("#musicianCardObj \{ background-color: #ffffff; border-radius: 8px; border: none; outline: none; \}"\)\n\s*else:\n\s*self\.setStyleSheet\("#musicianCardObj \{ background-color: #2d2d34; border-radius: 8px; border: none; outline: none; \}"\)',
    '',
    content,
    flags=re.DOTALL
)

# Update force_profile_selection loop to use properties instead of raw style sheets
force_selection_code = """    def force_profile_selection(self, card):
        import theme
        try:
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            from PySide6.QtGui import QColor
            
            for c in self.profile_cards:
                is_sel = (c == card)
                c.setProperty("selected", "true" if is_sel else "false")
                c.style().unpolish(c)
                c.style().polish(c)
                
                if is_sel:
                    shadow = QGraphicsDropShadowEffect(c)
                    if theme.CURRENT_MODE == "light":
                        shadow.setBlurRadius(20)
                        shadow.setColor(QColor(0, 0, 0, 70))
                        shadow.setOffset(0, 6)
                    else:
"""
content = re.sub(
    r'    def force_profile_selection\(self, card\):.*?else:\s*c\.setStyleSheet\("#musicianCardObj \{ background-color: #2d2d34; border-radius: 8px; border: none; outline: none; \}"\)\s*if is_sel:\s*shadow = QGraphicsDropShadowEffect\(c\)\s*if theme\.CURRENT_MODE == "light":\s*shadow\.setBlurRadius\(20\)\s*shadow\.setColor\(QColor\(0, 0, 0, 70\)\)\s*shadow\.setOffset\(0, 6\)\s*else:',
    force_selection_code,
    content,
    flags=re.DOTALL
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
