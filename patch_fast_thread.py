import os
import glob

files = glob.glob("*.scad")

fast_thread = """module Bulletproof_Thread(d, pitch, turns) {
    sphere_d = pitch * 0.8;
    // Blitzschnelles Gewinde via linear_extrude (Rendert in 0.1 Sekunden!)
    linear_extrude(height = pitch * turns, twist = -360 * turns, slices = turns * 36)
    translate([d / 2, 0])
    circle(d = sphere_d, $fn=16);
}"""

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
            
        import re
        # Finde das alte Bulletproof_Thread modul
        pattern = re.compile(r'module Bulletproof_Thread.*?^\}', re.MULTILINE | re.DOTALL)
        
        if pattern.search(content):
            content = pattern.sub(fast_thread, content)
            with open(filename, "w") as f:
                f.write(content)
