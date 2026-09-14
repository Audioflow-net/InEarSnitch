import os
import glob

files = glob.glob("*.scad")

solid_thread = """module Bulletproof_Thread(d, pitch, turns) {
    radius = d / 2; steps_per_turn = 24;
    angle_step = 360 / steps_per_turn; z_step = pitch / steps_per_turn;
    total_steps = turns * steps_per_turn; sphere_d = pitch * 0.8; 
    for (i = [0 : total_steps - 1]) {
        a1 = i * angle_step; z1 = i * z_step;
        a2 = (i + 1) * angle_step; z2 = (i + 1) * z_step;
        hull() {
            translate([radius * cos(a1), radius * sin(a1), z1]) sphere(d=sphere_d, $fn=8);
            translate([radius * cos(a2), radius * sin(a2), z2]) sphere(d=sphere_d, $fn=8);
        }
    }
}"""

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
            
        import re
        pattern = re.compile(r'module Bulletproof_Thread.*?^\}', re.MULTILINE | re.DOTALL)
        
        if pattern.search(content):
            content = pattern.sub(solid_thread, content)
            with open(filename, "w") as f:
                f.write(content)
