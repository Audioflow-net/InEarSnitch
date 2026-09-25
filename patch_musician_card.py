import re

with open("main.py", "r") as f:
    content = f.read()

old_layout = """    def _update_layout(self, width):
        from PySide6.QtWidgets import QBoxLayout
        # print(f"MusicianCard width: {width}")
        if width < 200:
            self.avatar.hide()
            self.role_lbl.hide()
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.name_lbl.setAlignment(Qt.AlignCenter)
        else:
            self.avatar.show()
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        import theme"""

new_layout = """    def _update_layout(self, width):
        from PySide6.QtWidgets import QBoxLayout
        # Always show avatar, but hide role if too compact
        self.avatar.show()
        if width < 140:
            self.role_lbl.hide()
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.name_lbl.setAlignment(Qt.AlignCenter)
        else:
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        import theme"""

content = content.replace(old_layout, new_layout)

with open("main.py", "w") as f:
    f.write(content)
