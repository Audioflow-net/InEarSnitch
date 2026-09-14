import os
import glob

files = glob.glob("*.scad")

safe_thread = """module Bulletproof_Thread(d, pitch, turns) {
    sphere_d = pitch; 
    // ACHTUNG: Kein HULL mehr! Nur noch überlappende Kugeln. 
    // Das ergibt ein "noppiges" Gewinde, was perfekt greift und OpenSCAD NIEMALS zum Absturz bringt.
    for(i=[0:10:turns*360]) {
        translate([(d/2)*cos(i), (d/2)*sin(i), i/360*pitch]) 
        sphere(d=sphere_d, $fn=8);
    }
}"""

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
            
        import re
        pattern = re.compile(r'module Bulletproof_Thread.*?^\}', re.MULTILINE | re.DOTALL)
        
        if pattern.search(content):
            content = pattern.sub(safe_thread, content)
            with open(filename, "w") as f:
                f.write(content)
