import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Add lbl_sub to __init__
pattern1 = r'''        self\.lbl = pg\.TextItem\(html='', anchor=\(0\.5, 0\.5\)\)
        self\.lbl\.setZValue\(100\)
        self\.lbl\.hide\(\)
        self\.lbl\.setParentItem\(self\.plot_widget\.getViewBox\(\)\)
        
        self\.sweeps = 1'''

replacement1 = r'''        self.lbl = pg.TextItem(html='', anchor=(0.5, 0.5))
        self.lbl.setZValue(100)
        self.lbl.hide()
        self.lbl.setParentItem(self.plot_widget.getViewBox())
        
        self.lbl_sub = pg.TextItem(html='', anchor=(0.5, 0.5))
        self.lbl_sub.setZValue(100)
        self.lbl_sub.hide()
        self.lbl_sub.setParentItem(self.plot_widget.getViewBox())
        
        self.sweeps = 1'''

code = re.sub(pattern1, replacement1, code)

# 2. Update start
pattern2 = r'''        self\.lbl\.show\(\)
        
        vb = self\.plot_widget\.getViewBox\(\)
        rect = vb\.boundingRect\(\)
        self\.lbl\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2\)
        
        self\.set_text\("SCANNING"\)'''

replacement2 = r'''        self.lbl.show()
        
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        self.lbl.setPos(rect.width()/2, rect.height()/2 - 40)
        self.lbl_sub.setPos(rect.width()/2, rect.height()/2 + 40)
        
        self.set_text("SCANNING")'''

code = re.sub(pattern2, replacement2, code)

# 3. Update set_text
pattern3 = r'''    def set_text\(self, txt\):
        accent = theme\.get_color\('accent'\)
        self\.lbl\.setHtml\(f'<div style="font-family: Arial; font-size: 64px; color: \{accent\}; font-weight: 900; letter-spacing: 5px; text-transform: uppercase;"><center>\{txt\}</center></div>'\)'''

replacement3 = r'''    def set_text(self, txt, sub_txt=""):
        accent = theme.get_color('accent')
        self.lbl.setHtml(f'<div style="font-family: Arial; font-size: 64px; color: {accent}; font-weight: 900; letter-spacing: 5px; text-transform: uppercase;"><center>{txt}</center></div>')
        if sub_txt:
            self.lbl_sub.setHtml(f'<div style="font-family: Arial; font-size: 64px; color: {accent}; font-weight: 900; letter-spacing: 5px;"><center>{sub_txt}</center></div>')
            self.lbl_sub.show()
        else:
            self.lbl_sub.hide()'''

code = re.sub(pattern3, replacement3, code)

# 4. Update update_anim_sync
pattern4 = r'''        self\.lbl\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2\)
        
        if self\.sweeps > 1:
            if getattr\(self, 'last_sweep_num', None\) != sweep_num:
                self\.set_text\(f"SCANNING<br>\{sweep_num\} / \{self\.sweeps\}"\)
                self\.last_sweep_num = sweep_num'''

replacement4 = r'''        if self.sweeps > 1:
            self.lbl.setPos(rect.width()/2, rect.height()/2 - 40)
            self.lbl_sub.setPos(rect.width()/2, rect.height()/2 + 40)
        else:
            self.lbl.setPos(rect.width()/2, rect.height()/2)
            
        if self.sweeps > 1:
            if getattr(self, 'last_sweep_num', None) != sweep_num:
                self.set_text("SCANNING", f"{sweep_num} / {self.sweeps}")
                self.last_sweep_num = sweep_num'''

code = re.sub(pattern4, replacement4, code)

# 5. Update stop
pattern5 = r'''    def stop\(self\):
        self\.sweep_line\.hide\(\)
        self\.region\.hide\(\)
        self\.lbl\.hide\(\)'''

replacement5 = r'''    def stop(self):
        self.sweep_line.hide()
        self.region.hide()
        self.lbl.hide()
        self.lbl_sub.hide()'''

code = re.sub(pattern5, replacement5, code)

with open("main.py", "w") as f:
    f.write(code)

print("Patched.")
