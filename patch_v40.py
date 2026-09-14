import re

with open("iem_rig_final.scad", "r") as f:
    content = f.read()

# Add the TPU components from V41/V44 to the bottom of the V40 file safely
tpu_code = """
// ----------------------------------------------------------------
// TPU UPGRADES V44 (MEMBRAN-TECHNOLOGIE FÜR CUSTOM IEMS)
// ----------------------------------------------------------------

module TPU_CIEM_Membrane() {
    difference() {
        union() {
            cylinder(d=45, h=0.8);
            translate([0, 0, 0.8]) cylinder(d1=45, d2=16, h=10);
            translate([0, 0, 10.8]) cylinder(d=16, h=15);
        }
        translate([0, 0, -1]) cylinder(d=3, h=3);
        translate([0, 0, 0.8]) cylinder(d1=42, d2=12.6, h=10);
        translate([0, 0, 10.8]) cylinder(d=12.6, h=16);
    }
}

module TPU_Bristle_Pad() {
    // DAS ULTIMATIVE WEICHE KISSEN! (Wie auf deinem Foto!)
    // Generiert hunderte kleine TPU-Säulen, die sich wie eine Bürste
    // um jede krumme Custom IEM Rückseite biegen. Absolut kratzfrei!
    union() {
        // Die feste Basis und der Zapfen (rastet in den Slider ein)
        cylinder(d=40, h=3);
        translate([0, 0, 3]) cylinder(d=14.5, h=12);
        translate([0, 0, 15]) sphere(d=14.5); // Kugelgelenk
        
        // Die weiche Bürsten-Struktur (nach unten gerichtet)
        for (x = [-17 : 2.5 : 17]) {
            for (y = [-17 : 2.5 : 17]) {
                if (x*x + y*y < 18*18) {
                    translate([x, y, -10]) cylinder(d=1.2, h=10);
                }
            }
        }
    }
}
"""

with open("iem_rig_final.scad", "w") as f:
    f.write(content + "\n" + tpu_code)
