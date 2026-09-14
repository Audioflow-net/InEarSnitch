import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''    def start\(self, sweeps\):
        self\.sweeps = sweeps
        self\.region\.show\(\)
        self\.sweep_line\.show\(\)
        self\.lbl\.show\(\)
        
        vb = self\.plot_widget\.getViewBox\(\)
        rect = vb\.boundingRect\(\)
        self\.lbl\.setPos\(rect\.width\(\)/2, rect\.height\(\)/2\)
        
        self\.set_text\("SCANNING"\)'''

replacement = r'''    def start(self, sweeps):
        self.sweeps = sweeps
        self.last_sweep_num = None
        self.region.show()
        self.sweep_line.show()
        self.lbl.show()
        
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        self.lbl.setPos(rect.width()/2, rect.height()/2)
        
        self.set_text("SCANNING")'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Start patched.")
