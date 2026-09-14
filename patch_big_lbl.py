import re

with open('main.py', 'r') as f:
    content = f.read()

# Replace the text item update logic
old_lbl_logic = """            # Anchor is (0.5, 1.0) - bottom center
            self.rta_big_lbl.setPos(w/2, rect.height() - 20)
            divider = "<br>" if seal_html and depth_html else ""
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: {font_size}px; background-color: rgba(0,0,0,150); padding: 8px; border-radius: 8px;'><center>{seal_html}{divider}{depth_html}</center></div>")
            self.rta_big_lbl.show()"""

new_lbl_logic = """            # Anchor is (0.5, 1.0) - bottom center
            self.rta_big_lbl.setPos(w/2, rect.height() - 20)
            divider = "<br>" if seal_html and depth_html else ""
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: {font_size}px; background-color: rgba(0,0,0,150); padding: 8px; border-radius: 8px;'><center>{seal_html}{divider}{depth_html}</center></div>")
            
            # Hide it if helper is off or if there is no text to show
            if not seal_html and not depth_html:
                self.rta_big_lbl.hide()
            elif hasattr(self, 'chk_rta_helper') and not self.chk_rta_helper.isChecked():
                self.rta_big_lbl.hide()
            else:
                self.rta_big_lbl.show()"""

content = content.replace(old_lbl_logic, new_lbl_logic)

with open('main.py', 'w') as f:
    f.write(content)
