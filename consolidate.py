import os
import glob

safe_thread = """module Bulletproof_Thread(d, pitch, turns) {
    step_angle = 5; 
    cube_len = (d * 3.1415 / (360 / step_angle)) * 2.0; 
    for(i=[0:step_angle:turns*360]) {
        translate([(d/2)*cos(i), (d/2)*sin(i), i/360*pitch])
        rotate([0, 0, i])
        cube([pitch * 2.0, cube_len, pitch * 0.8], center=true);
    }
}"""

v5_code = """$fn = 60;
part = "pla_set"; // render all 3 PLA parts side-by-side
""" + safe_thread + """
module Base() {
    difference() {
        union() {
            translate([0, 0, -2]) cylinder(d=56, h=2, $fn=6);
            cylinder(d=48.5, h=11.5); Bulletproof_Thread(d=46.0, pitch=2.0, turns=5.7); 
        }
        translate([0, 0, -10]) cylinder(d=21.5, h=8); 
        translate([0, 0, -10]) Bulletproof_Thread(d=21.3, pitch=0.5, turns=16); 
        translate([0, 0, -2]) cylinder(d=16, h=2.1);
        translate([0, 0, 0]) cylinder(d1=15, d2=38, h=11.1); 
    }
}
module Washer() {
    difference() { cylinder(d=41, h=0.6); translate([0, 0, -1]) cylinder(d=38, h=3); }
}
module Nut(twist_down = 0) {
    translate([0, 0, -twist_down]) difference() {
        union() {
            cylinder(d=56, h=12);
            for(a=[0:10:359]) rotate([0, 0, a]) translate([28, 0, 6]) cylinder(d=1.5, h=12, center=true, $fn=12);
        }
        translate([0, 0, -1]) {
            cylinder(d=49.0, h=12); Bulletproof_Thread(d=47.5, pitch=2.0, turns=6.5);
        }
        translate([0, 0, 10.5]) cylinder(d=38, h=5);
    }
}
if (part == "pla_set") {
    translate([-35, 0, 0]) Base();
    translate([0, -40, 0]) Washer();
    translate([35, 0, 0]) Nut(0);
}
"""

v4_code = """$fn = 60;
part = "pla_set"; // render all 3 PLA parts side-by-side
""" + safe_thread + """
module Base() {
    difference() {
        union() {
            translate([0, 0, -2]) cylinder(d=46, h=2, $fn=6);
            cylinder(d=38.5, h=7.5); Bulletproof_Thread(d=36.8, pitch=1.5, turns=5.0); 
        }
        translate([0, 0, -10]) cylinder(d=21.5, h=8); 
        translate([0, 0, -10]) Bulletproof_Thread(d=21.3, pitch=0.5, turns=16); 
        translate([0, 0, -2]) cylinder(d=16, h=2.1);
        translate([0, 0, 0]) cylinder(d1=15, d2=31.2, h=7.1); 
    }
}
module Washer() {
    difference() { cylinder(d=35, h=0.6); translate([0, 0, -1]) cylinder(d=32, h=3); }
}
module Nut(twist_down = 0) {
    translate([0, 0, -twist_down]) difference() {
        union() {
            cylinder(d=46, h=8);
            for(a=[0:10:359]) rotate([0, 0, a]) translate([23, 0, 4]) cylinder(d=1.5, h=8, center=true, $fn=12);
        }
        translate([0, 0, -1]) {
            cylinder(d=39.0, h=8); Bulletproof_Thread(d=37.5, pitch=1.5, turns=6.0);
        }
        translate([0, 0, 6.5]) cylinder(d=32, h=5);
    }
}
if (part == "pla_set") {
    translate([-30, 0, 0]) Base();
    translate([0, -35, 0]) Washer();
    translate([30, 0, 0]) Nut(0);
}
"""

with open("PRINT_ME_V5_PLA.scad", "w") as f: f.write(v5_code)
with open("PRINT_ME_V4_PLA.scad", "w") as f: f.write(v4_code)

# Cleanup isolated files
files_to_remove = glob.glob("*_BASE.scad") + glob.glob("*_NUT.scad") + glob.glob("*_WASHER.scad")
for f in files_to_remove:
    os.remove(f)

