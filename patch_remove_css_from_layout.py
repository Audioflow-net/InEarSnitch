import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """        else:
            # Normal Mode: Avatar left, text & grid right
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.layout.setAlignment(self.avatar, Qt.AlignLeft | Qt.AlignTop)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.role_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        import theme
        if theme.CURRENT_MODE == "light":
            self.setStyleSheet("#musicianCardObj { background-color: #ffffff; border-radius: 8px; border: none; outline: none; }")
        else:
            self.setStyleSheet("#musicianCardObj { background-color: #2d2d34; border-radius: 8px; border: none; outline: none; }")
        # AvatarButtons keep their own click handlers (select_iem)"""

new_logic = """        else:
            # Normal Mode: Avatar left, text & grid right
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.layout.setAlignment(self.avatar, Qt.AlignLeft | Qt.AlignTop)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.role_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
        # AvatarButtons keep their own click handlers (select_iem)"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
