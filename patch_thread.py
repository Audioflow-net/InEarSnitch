import re

with open("iem_rig_final.scad", "r") as f:
    content = f.read()

# Add the Bulletproof_Thread module and configurable diameter
thread_mod = """
// ----------------------------------------------------------------
// NEUES 100% SICHERES GEWINDE-MODUL
// ----------------------------------------------------------------
// Wenn du später die exakten Maße hast, kannst du sie hier einfach ändern!
coupler_thread_d = 23.0; // <- HIER DEN DURCHMESSER ANPASSEN (war 22.3, jetzt 23.0 zum Testen)
coupler_thread_pitch = 0.5; // Steigung

module Bulletproof_Thread(d, h, pitch) {
    r_center = (d - pitch*0.5) / 2;
    steps_per_turn = 45; 
    total_turns = h / pitch;
    total_steps = floor(total_turns * steps_per_turn);
    
    union() {
        cylinder(d=d - pitch*1.2, h=h, $fn=60);
        for (i=[0 : total_steps-1]) {
            hull() {
                translate([r_center * cos(i * 360/steps_per_turn), r_center * sin(i * 360/steps_per_turn), i * (pitch/steps_per_turn)]) sphere(d=pitch*0.8, $fn=8);
                translate([r_center * cos((i+1) * 360/steps_per_turn), r_center * sin((i+1) * 360/steps_per_turn), (i+1) * (pitch/steps_per_turn)]) sphere(d=pitch*0.8, $fn=8);
            }
        }
    }
}
"""

content = content.replace("// HILFS-MODULE", thread_mod + "\n// HILFS-MODULE")

# In base_body, replace the old coupler hole with the new thread!
# wait, iem_rig_v9.scad doesn't have a threaded hole for the coupler, it just has a 24.5mm hole for the fat part.
# Let's just put it in the Main_Chamber (base_body).
