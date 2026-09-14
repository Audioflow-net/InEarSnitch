import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# Ersetze die TPU Donut Geometrie mit der neuen Schutz-Lippe
old_tpu = """module TPU_Donut(size="M") {
    inner_d = (size == "S") ? 7.5 : (size == "M") ? 10.0 : 12.5;
    
    difference() {
        cylinder(d1=11, d2=22.5, h=4); // Konisch
        translate([0, 0, -1]) cylinder(d=inner_d, h=6); // Das Loch
    }
}"""

new_tpu = """module TPU_Donut(size="M") {
    inner_d = (size == "S") ? 7.5 : (size == "M") ? 10.0 : 12.5;
    
    difference() {
        cylinder(d1=11, d2=22.5, h=4); // Konisch
        
        // Das Loch für das CIEM (lässt unten 0.4mm TPU als Kratz-Schutz stehen!)
        translate([0, 0, 0.4]) cylinder(d=inner_d, h=6); 
        
        // Das Schall-Loch ganz unten (Exakt 7.5mm wie das Mikrofonloch)
        translate([0, 0, -1]) cylinder(d=7.5, h=6);
    }
}"""

content = content.replace(old_tpu, new_tpu)

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
