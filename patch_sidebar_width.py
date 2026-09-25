import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Update profile_bar width
old_bar = """        profile_bar.setMinimumWidth(170)
        profile_bar.setMaximumWidth(280)"""

new_bar = """        profile_bar.setMinimumWidth(220)
        profile_bar.setMaximumWidth(320)"""

content = content.replace(old_bar, new_bar)

# 2. Update MusicianCard compact mode to keep avatar visible but layout vertical
old_card = """        self.avatar.show()
        if width < 140:
            self.role_lbl.hide()
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.name_lbl.setAlignment(Qt.AlignCenter)
        else:
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)"""

new_card = """        self.avatar.show()
        if width < 185:
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

content = content.replace(old_card, new_card)

with open("main.py", "w") as f:
    f.write(content)
