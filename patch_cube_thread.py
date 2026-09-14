import os
import glob

files = glob.glob("*.scad")

cube_thread = """module Bulletproof_Thread(d, pitch, turns) {
    // Die ultimative Lösung: Überlappende Quader! 
    // Garantiert 100% zusammenhängend (keine Lücken mehr),
    // simuliert ein durchgehendes Gewinde, stürzt NIEMALS ab.
    step_angle = 5; // 72 Quader pro Umdrehung
    cube_len = (d * 3.1415 / (360 / step_angle)) * 1.5; // Groß genug zum Überlappen
    
    for(i=[0:step_angle:turns*360]) {
        translate([(d/2)*cos(i), (d/2)*sin(i), i/360*pitch])
        rotate([0, 0, i + 90])
        cube([pitch * 0.8, cube_len, pitch * 0.8], center=true);
    }
}"""

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
            
        import re
        pattern = re.compile(r'module Bulletproof_Thread.*?^\}', re.MULTILINE | re.DOTALL)
        
        if pattern.search(content):
            content = pattern.sub(cube_thread, content)
            with open(filename, "w") as f:
                f.write(content)
