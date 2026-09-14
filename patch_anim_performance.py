import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''    def update_anim_sync\(self, t_elapsed, sweep_num\):
        import math
        
        # Center the HUD text dynamically
        vb = self\.plot_widget\.getViewBox\(\)
        rect = vb\.boundingRect\(\)
        self\.lbl\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2\)
        
        if self\.sweeps > 1:
            self\.set_text\(f"SCANNING<br><span style=\\"font-size: 48px;\\">\{sweep_num\}/\{self\.sweeps\}</span>"\)'''

replacement = r'''    def update_anim_sync(self, t_elapsed, sweep_num):
        import math
        
        # Center the HUD text dynamically
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        self.lbl.setPos(rect.width()/2, rect.height()/2)
        
        if self.sweeps > 1:
            if getattr(self, 'last_sweep_num', None) != sweep_num:
                self.set_text(f"SCANNING<br><span style=\"font-size: 48px;\">{sweep_num}/{self.sweeps}</span>")
                self.last_sweep_num = sweep_num'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Performance patched.")
