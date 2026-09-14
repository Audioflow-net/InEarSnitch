import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Wanne Cut & Massive L-Track Ears
old_wanne = """        difference() {
            translate([2.4, 2.4, 34.0]) rounded_pocket(box_w - 4.8, box_d - 4.8, 4.1, r=2);
            // HINGE EARS (Ohren-Schutz): Verhindert, dass die Wanne die hinteren Ecken wegschneidet!
            // Das lässt massive 5.2mm dicke Blöcke stehen, in denen das Scharnier-Dach leben kann.
            translate([0, box_d - 12, 33]) cube([5.2, 15, 10]);
            translate([box_w - 5.2, box_d - 12, 33]) cube([5.2, 15, 10]);
        }"""
new_wanne = """        difference() {
            translate([2.4, 2.4, 34.0]) rounded_pocket(box_w - 4.8, box_d - 4.8, 4.1, r=2);
            // HINGE EARS: Massive 6.0mm Blöcke hinten für die L-Track Führung!
            translate([0, box_d - 13, 33]) cube([6.0, 15, 10]);
            translate([box_w - 6.0, box_d - 13, 33]) cube([6.0, 15, 10]);
        }
        
        // CONTINUOUS ROOF: Die "Struktur drüber über die ganze Breite" (Z=36 bis 37)
        // Verhindert das Hochklappen des Deckels, wenn er ganz nach hinten geschoben ist!
        color("#D0D0D0") translate([6.0, box_d - 4.0, 36.0]) cube([box_w - 12.0, 4.0, 1.0]);"""
content = content.replace(old_wanne, new_wanne)

# 2. Base Case: L-Track Slots (Replacing the Keyed Hinge cylinders)
old_hinge_cyls = """        // KEYED HINGE: Vertikaler Schlitz mit Dach und 1.8mm Spalt!
        // Liegt jetzt absolut sicher eingegossen in den massiven 5.2mm Hinge Ears (X=3.5)
        translate([3.5, pin_y, 5]) cylinder(d=3.2, h=31.0, $fn=16);
        translate([box_w - 3.5, pin_y, 5]) cylinder(d=3.2, h=31.0, $fn=16);
        
        // Der 2.1mm breite Spalt im Dach (Gibt dem 1.6mm dicken D-Pin perfekten FDM-Spielraum)
        translate([3.5, pin_y, 36.5]) cube([10, 2.1, 2.0], center=true);
        translate([box_w - 3.5, pin_y, 36.5]) cube([10, 2.1, 2.0], center=true);"""
new_hinge_cyls = """        // L-TRACK FÜHRUNG (Horizontaler Slide & Vertikaler Drop)
        // Linke Spur (In das 6mm Ohr gefräst, 2.5mm tief)
        translate([3.5, box_d - 6.5, 35.5]) cube([5.0, 6.0, 3.2], center=true); // Horizontal (Lock-Position)
        translate([3.5, box_d - 9.5, 31.0]) cube([5.0, 3.2, 12.0], center=true); // Vertikal (Drop-Position)
        
        // Rechte Spur
        translate([box_w - 3.5, box_d - 6.5, 35.5]) cube([5.0, 6.0, 3.2], center=true);
        translate([box_w - 3.5, box_d - 9.5, 31.0]) cube([5.0, 3.2, 12.0], center=true);"""
content = content.replace(old_hinge_cyls, new_hinge_cyls)

# 3. Stage Lid: Complete replacement
old_stage_lid = re.search(r'module stage_lid\(\) \{.*?\n\}\n', content, re.DOTALL).group(0)

new_stage_lid = """module stage_lid() {
    lid_w = box_w - 5.4;
    lid_d = box_d - 5.4;
    tongue_w = box_w - 12.4; // 0.4mm Clearance zu den 6.0mm Ears
    
    color("#B0B0B0")
    union() {
        difference() {
            translate([2.7, 2.7, 0]) rounded_pocket(lid_w, lid_d, lid_h, r=1.8);
            
            // HINGE NOTCHES (Aussparungen hinten, um die schmale Zunge zu bilden)
            translate([0, lid_d - 10, -1]) cube([6.2, 15, 10]);
            translate([box_w - 6.2, lid_d - 10, -1]) cube([6.2, 15, 10]);
            
            // REAR FLANGE CUTOUT (Macht den hinteren Rand nur 2mm dick, damit er unter das Roof passt!)
            translate([6.2, lid_d - 3.0, 2.0]) cube([tongue_w, 4.0, 2.0]);
            
            // Label auf der OBERSEITE
            translate([box_w/2 - 30, 15, lid_h - 0.6]) cube([60, 15, 0.7]);
            
            // WAFFLE-GRID
            translate([box_w/2, box_d/2, 0]) 
                intersection() {
                    hex_grid_centered(124, 96, 15.0, 1.8); 
                    translate([0, 0, 0.8]) cube([200, 200, 1.6], center=true);
                }
        }
        
        // EUROBOX LATCH: Der flexible Scharnier-Schnapper
        union() {
            translate([box_w/2, 0.8, -4.75]) cube([31.0, 1.6, 15.5], center=true);
            translate([box_w/2, 2.0, -11.5]) cube([31.0, 2.4, 2.0], center=true);
            translate([box_w/2, -0.3, -3.0]) cube([31.0, 0.6, 2.0], center=true);
        }
        
        // STANDARD PINS (Für L-Track Führung)
        // Keine D-Form mehr nötig. Einfache Zylinder, die in der Führung gleiten.
        translate([6.2, lid_d - 1.5, 1.5]) rotate([0, -90, 0]) cylinder(d=3.0, h=3.0, $fn=24);
        translate([box_w - 6.2, lid_d - 1.5, 1.5]) rotate([0, 90, 0]) cylinder(d=3.0, h=3.0, $fn=24);
    }
}
"""
content = content.replace(old_stage_lid, new_stage_lid)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
