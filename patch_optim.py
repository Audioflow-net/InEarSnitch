import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''        # Center the HUD text dynamically
        vb = self\.plot_widget\.getViewBox\(\)
        rect = vb\.boundingRect\(\)
        if self\.sweeps > 1:
            self\.lbl\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2 - 40\)
            self\.lbl_sub\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2 \+ 40\)
        else:
            self\.lbl\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2\)'''

replacement = r'''        # Center the HUD text dynamically
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        if getattr(self, 'last_rect', None) != rect:
            if self.sweeps > 1:
                self.lbl.setPos(rect.width()/2, rect.height()/2 - 40)
                self.lbl_sub.setPos(rect.width()/2, rect.height()/2 + 40)
            else:
                self.lbl.setPos(rect.width()/2, rect.height()/2)
            self.last_rect = rect'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Patched with optimization.")
