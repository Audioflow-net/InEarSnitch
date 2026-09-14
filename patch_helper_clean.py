import sys

with open('main.py', 'r') as f:
    content = f.read()

old_html = """            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: 28px; background-color: rgba(0,0,0,150); padding: 10px; border-radius: 8px;'><center>{seal_html} &nbsp;&nbsp;|&nbsp;&nbsp; {depth_html}</center></div>")"""

new_html = """            divider = "&nbsp;&nbsp;|&nbsp;&nbsp;" if seal_html and depth_html else ""
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: 28px; background-color: rgba(0,0,0,150); padding: 10px; border-radius: 8px;'><center>{seal_html} {divider} {depth_html}</center></div>")"""

content = content.replace(old_html, new_html)

with open('main.py', 'w') as f:
    f.write(content)
