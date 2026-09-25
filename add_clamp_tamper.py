import re

with open('/Users/ben/Desktop/InEarSnitch/CIEM_XL_Adapter_Molds.scad', 'r') as f:
    content = f.read()

clamp_piston_code = """
module piston_clamp(clamp_d=7.0, body_d=9.4, label="V27-C7") {
    shaft_len = 7.61 + extra_v27_length;
    z_equator = 9.6 - shaft_len; // -1.01
    z_tip = z_equator - 2.0;     // -3.01

    difference() {
        union() {
            // Deckel
            translate([0,0, 14.1]) linear_extrude(3) square([29, 29], center=true);
            
            // Acoustic Bore Flansch-Bereich (7.5mm)
            translate([0,0,9.6]) cylinder(d=7.5, h=4.51, $fn=64);
            
            // Der weite 9.4mm Body (damit der IEM tief rutschen kann)
            // Geht von Z = 0.5 bis Z = 9.6
            translate([0,0, 0.5]) cylinder(d=body_d, h=9.6 - 0.5, $fn=64);
            
            // Konischer Übergang von 7.0 auf 9.4
            translate([0,0, z_equator]) cylinder(d1=clamp_d, d2=body_d, h=0.5 - z_equator, $fn=64);
            
            // Das enge 7.0mm Clamp-Loch an der Eintrittslippe
            translate([0,0, z_tip]) cylinder(d=clamp_d, h=z_equator - z_tip, $fn=64);
            
            // Ankerloch
            translate([0,0,-8.1]) cylinder(d=4.0, h=8.1 + z_tip, $fn=64);
        }
        
        translate([0, -12, 16.5]) linear_extrude(2) text(label, size=3.5, halign="center", valign="center", font="Arial:style=Bold");
        
        // Blind-Kompressionstasche
        translate([0,0,14.09]) difference() {
            cylinder(d=8.1, h=1.5, $fn=64);
            cylinder(d=7.5, h=1.5, $fn=64); 
        }
    }
}
"""

# Insert it right before the render modules
content = content.replace('// ==========================================\n// RENDER MODULE', clamp_piston_code + '\n// ==========================================\n// RENDER MODULE')

old_layout = r'translate\(\[\s*0,\s*-35,\s*0\]\) color\("Gold"\) piston_v27\(hole_size=9.4, label="V27-9.4"\);'
new_layout = 'translate([  0, -35, 0]) color("Gold") piston_clamp(clamp_d=7.0, body_d=9.4, label="V27-C7");'

content = re.sub(old_layout, new_layout, content)

with open('/Users/ben/Desktop/InEarSnitch/CIEM_XL_Adapter_Molds.scad', 'w') as f:
    f.write(content)

