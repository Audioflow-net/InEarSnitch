import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# 1. Entferne die Lippe aus dem TPU_Donut (es wird wieder ein durchgehendes Rohr)
old_tpu = """module TPU_Donut(size="M") {
    inner_d = (size == "S") ? 7.5 : (size == "M") ? 10.0 : 12.5;
    
    difference() {
        cylinder(d1=15, d2=23.8, h=4); // Breiterer Fuß, damit die Lippe nicht abreißt
        
        // Das Loch für das CIEM (lässt unten 0.4mm TPU als Kratz-Schutz stehen!)
        translate([0, 0, 0.4]) cylinder(d=inner_d, h=6); 
        
        // Das Schall-Loch ganz unten (Exakt 5mm wie die Coupler-Grube)
        translate([0, 0, -1]) cylinder(d=5.0, h=6); // Exakt 5mm wie die Coupler-Grube
    }
}"""

new_tpu = """module TPU_Donut(size="M") {
    inner_d = (size == "S") ? 7.5 : (size == "M") ? 10.0 : 12.5;
    difference() {
        cylinder(d1=15, d2=23.8, h=4);
        // Durchgehendes Loch (Reine Röhre ohne Boden)
        translate([0, 0, -1]) cylinder(d=inner_d, h=6);
    }
}

// BAUTEIL 2b: DIE SEPARATE SCHUTZSCHEIBE (TPU)
module TPU_Schutzscheibe() {
    difference() {
        cylinder(d=15, h=0.4); // 0.4mm dick, 15mm breit (passt exakt aufs Metall)
        translate([0, 0, -1]) cylinder(d=5.0, h=2); // 5mm Schall-Loch
    }
}"""

content = content.replace(old_tpu, new_tpu)

# 2. Füge die Schutzscheibe zur "tpu_set" Szene hinzu
old_export = """else if (part == "tpu_set") {
    // Alle 3 TPU Donuts auf einmal für den Slicer
    translate([-40, 0, 0]) TPU_Donut("S");
    translate([0, 0, 0]) TPU_Donut("M");
    translate([40, 0, 0]) TPU_Donut("L");
}"""

new_export = """else if (part == "tpu_set") {
    // Alle 3 TPU Donuts
    translate([-40, 0, 0]) TPU_Donut("S");
    translate([0, 0, 0]) TPU_Donut("M");
    translate([40, 0, 0]) TPU_Donut("L");
    // Und die separate TPU Schutzscheibe daneben!
    translate([0, -30, 0]) TPU_Schutzscheibe();
}"""

content = content.replace(old_export, new_export)

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
