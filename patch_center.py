import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''    def set_text\(self, txt\):
        accent = theme\.get_color\('accent'\)
        self\.lbl\.setHtml\(f'<div align="center" style="font-family: Arial; font-size: 64px; color: \{accent\}; font-weight: 900; letter-spacing: 5px; text-transform: uppercase;">\{txt\}</div>'\)'''

replacement = r'''    def set_text(self, txt):
        accent = theme.get_color('accent')
        self.lbl.setHtml(f'<div style="font-family: Arial; font-size: 64px; color: {accent}; font-weight: 900; letter-spacing: 5px; text-transform: uppercase;"><center>{txt}</center></div>')'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Patched.")
