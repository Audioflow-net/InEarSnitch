import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """        if width < 185:
            # Compact Mode: Avatar on top, centered text, grid below
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.name_lbl.setAlignment(Qt.AlignCenter)
            self.role_lbl.setAlignment(Qt.AlignCenter)
            self.avatar.setAlignment(Qt.AlignCenter)
        else:
            # Normal Mode: Avatar left, text & grid right
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.role_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)"""

new_logic = """        if width < 185:
            # Compact Mode: Avatar on top, centered text, grid below
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.layout.setAlignment(self.avatar, Qt.AlignCenter)
            self.name_lbl.setAlignment(Qt.AlignCenter)
            self.role_lbl.setAlignment(Qt.AlignCenter)
        else:
            # Normal Mode: Avatar left, text & grid right
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.layout.setAlignment(self.avatar, Qt.AlignLeft | Qt.AlignTop)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.role_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
