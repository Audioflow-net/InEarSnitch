import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Replace the square flange cutout with a printable chamfer cutout
old_flange = r'// REAR FLANGE CUTOUT \(Macht den hinteren Rand nur 2mm dick, damit er unter das Roof passt!\)\n\s*translate\(\[6\.2, lid_d - 3\.0, 2\.0\]\) cube\(\[tongue_w, 4\.0, 2\.0\]\);'

new_flange = """// REAR FLANGE CUTOUT (Macht den hinteren Rand nur 2mm dick, damit er unter das Roof passt!)
            // Wir verwenden ein hull(), um eine 45-Grad-Schräge zu erzeugen. 
            // So lässt sich der Deckel umgedreht PERFEKT ohne Support drucken!
            translate([6.2, 0, 0]) hull() {
                translate([0, lid_d - 3.0, 3.0]) cube([tongue_w, 3.0, 1.0]);
                translate([0, lid_d - 0.1, 2.0]) cube([tongue_w, 0.1, 2.0]);
            }"""

content = re.sub(old_flange, new_flange, content)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
