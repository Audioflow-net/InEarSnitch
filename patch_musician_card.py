import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'self.current_iem_name = iems[0][1] if iems else "Unknown IEM"',
    'self.current_iem_name = (iems[0][4] if (iems and len(iems[0])>4 and iems[0][4]) else iems[0][1]) if iems else "Unknown IEM"'
)

code = code.replace(
    'for iem_id, iem_name, pic_path, abbr in iems:',
    'for iem_id, iem_name, pic_path, abbr, custom_name in iems:'
)

code = code.replace(
    'btn = AvatarButton(iem_id, iem_name, pic_path, abbr, self)',
    'display_name = custom_name if custom_name else iem_name\n            btn = AvatarButton(iem_id, display_name, pic_path, abbr, self)'
)

with open("main.py", "w") as f:
    f.write(code)

print("Musician card patched.")
