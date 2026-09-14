import re

with open("profile_ui.py", "r") as f:
    code = f.read()

# 1. Add margins to content_layout
old_margins = "content_layout.setContentsMargins(0, 0, 0, 0)"
new_margins = "content_layout.setContentsMargins(30, 30, 30, 30)"
code = code.replace(old_margins, new_margins)

# 2. Increase ProfilePicWidget size from 110 to 160
old_pic = 'self.pic_widget = ProfilePicWidget(size=110, placeholder="Add Photo")'
new_pic = 'self.pic_widget = ProfilePicWidget(size=160, placeholder="Add Photo")'
code = code.replace(old_pic, new_pic)

with open("profile_ui.py", "w") as f:
    f.write(code)

print("Profile layout patched.")
