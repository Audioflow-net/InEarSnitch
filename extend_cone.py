with open("V27_MASTER_COLLECTION.scad", "r") as f:
    content = f.read()

import re

# 1. Update outer_cavity_cone
old_cavity = """module outer_cavity_cone() {
    // UPSIDE-DOWN DESIGN (Flansch ist OBEN!)
    // Schmale Spitze des Cone unten am Boden:
    translate([0,0,0]) cylinder(d1=4.0, d2=13.0, h=9.61, $fn=64); 
    // Der dicke 20mm Flansch liegt oben am Deckel:
    translate([0,0,9.6]) cylinder(d=20.0, h=4.51, $fn=64); 
    // 2.5mm Ankerloch tief unten im Boden für den Piston:
    translate([0,0,-3.1]) cylinder(d=2.5, h=3.2, $fn=64); 
}"""

new_cavity = """module outer_cavity_cone() {
    // UPSIDE-DOWN DESIGN (Flansch ist OBEN!)
    // EXTRA LANG: Zieht sich tief in den Block bis Z=-5.0 (Gesamte Cone-Länge = 14.6 mm!)
    translate([0,0,-5.0]) cylinder(d1=4.0, d2=13.0, h=14.61, $fn=64); 
    // Der dicke 20mm Flansch liegt oben am Deckel (Z=9.6 bis 14.1)
    translate([0,0,9.6]) cylinder(d=20.0, h=4.51, $fn=64); 
    // 2.5mm Ankerloch bohrt sich jetzt komplett durch den Boden (Z=-8.1), perfekt als Entlüftung und "Witness Pin"
    translate([0,0,-8.1]) cylinder(d=2.5, h=3.2, $fn=64); 
}"""

content = content.replace(old_cavity, new_cavity)

# 2. Update piston_cone_thin
old_piston = """module piston_cone_thin() {
    difference() {
        union() {
            // Deckel (V27 Standard 33.8mm für die Sleeve)
            translate([0,0, 14.1]) cylinder(d=33.8, h=3, $fn=64); 
            // 7.5mm Akustik-Bohrung sitzt jetzt OBEN im Flansch
            translate([0,0,9.6]) cylinder(d=7.5, h=4.51, $fn=64); 
            // Innerer Cone (von 7.5mm oben auf 2.5mm unten)
            translate([0,0,0]) cylinder(d1=2.5, d2=7.5, h=9.61, $fn=64); 
            // Unterer Anchor Pin (2.5mm)
            translate([0,0,-3.1]) cylinder(d=2.5, h=3.11, $fn=64); 
        }
        // Entlüftungslöcher (Radius 8, da 20mm Flansch drunter ist)
        for(a=[0:90:270]) rotate([0,0,a]) translate([8, 0, 12]) cylinder(d=2.5, h=10, $fn=32);
        translate([0, -12, 16.1]) linear_extrude(2) text("V29-C", size=4, halign="center", valign="center", font="Arial:style=Bold");
    }
}"""

new_piston = """module piston_cone_thin() {
    difference() {
        union() {
            // Deckel (V27 Standard 33.8mm für die Sleeve)
            translate([0,0, 14.1]) cylinder(d=33.8, h=3, $fn=64); 
            // 7.5mm Akustik-Bohrung sitzt jetzt OBEN im Flansch
            translate([0,0,9.6]) cylinder(d=7.5, h=4.51, $fn=64); 
            // Innerer Cone, jetzt 5mm länger (Z=-5.0 bis 9.6)
            translate([0,0,-5.0]) cylinder(d1=2.5, d2=7.5, h=14.61, $fn=64); 
            // Unterer Anchor Pin (2.5mm), schließt unten bündig mit dem Block ab
            translate([0,0,-8.1]) cylinder(d=2.5, h=3.11, $fn=64); 
        }
        // Entlüftungslöcher (Radius 8, da 20mm Flansch drunter ist)
        for(a=[0:90:270]) rotate([0,0,a]) translate([8, 0, 12]) cylinder(d=2.5, h=10, $fn=32);
        translate([0, -12, 16.1]) linear_extrude(2) text("V29-C", size=4, halign="center", valign="center", font="Arial:style=Bold");
    }
}"""

content = content.replace(old_piston, new_piston)

with open("V27_MASTER_COLLECTION.scad", "w") as f:
    f.write(content)

print("Done")
