import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Wanne, Ears, Vertical Track, and Deep Pocket
old_wanne_block = re.search(r'// Wanne \(Aussparung.*?// EUROBOX LATCH', content, re.DOTALL).group(0)

new_wanne_block = """// Wanne (Aussparung für den Deckel - Flach aufliegend)
        difference() {
            translate([2.4, 2.4, 34.0]) rounded_pocket(box_w - 4.8, box_d - 4.8, 4.1, r=2);
            // HINGE EARS: Massive 6.0mm Blöcke hinten für das Zapfen-Gelenk
            translate([0, box_d - 13, 33]) cube([6.0, 15, 10]);
            translate([box_w - 6.0, box_d - 13, 33]) cube([6.0, 15, 10]);
        }
        
        // POCKET DOOR SCHACHT (Hier fällt der Deckel senkrecht hinein!)
        // Breite: 5mm (für 3mm Deckel). Z geht tief runter bis Z=4.0
        translate([2.4, 117.5, 4.0]) cube([box_w - 4.8, 5.0, 30.0]);
        
        // VERTIKALE FÜHRUNG (Die Kulisse für die Zapfen)
        // Die Zapfen sitzen immer bei Y=120.0. Oben (Z=34.5) ist die Kiste zu.
        translate([3.5, 120.0, 19.25]) cube([5.0, 3.2, 30.5], center=true); // Linke Spur (Z=4.0 bis 34.5)
        translate([box_w - 3.5, 120.0, 19.25]) cube([5.0, 3.2, 30.5], center=true); // Rechte Spur
        
        // EUROBOX LATCH"""
content = content.replace(old_wanne_block, new_wanne_block)


# 2. Stage Lid: Remove Flange Cutout, Move Pins
old_stage_lid = re.search(r'module stage_lid\(\) \{.*?\n\}\n', content, re.DOTALL).group(0)

new_stage_lid = """module stage_lid() {
    lid_w = box_w - 5.4;
    lid_d = box_d - 5.4; // = 120.2
    
    color("#B0B0B0")
    union() {
        difference() {
            translate([2.7, 2.7, 0]) rounded_pocket(lid_w, lid_d, lid_h, r=1.8);
            
            // HINGE NOTCHES (Aussparungen hinten, um die schmale Zunge zu bilden)
            translate([0, lid_d - 10, -1]) cube([6.2, 15, 10]);
            translate([box_w - 6.2, lid_d - 10, -1]) cube([6.2, 15, 10]);
            
            // Label auf der OBERSEITE
            translate([box_w/2 - 30, 15, lid_h - 0.6]) cube([60, 15, 0.7]);
            
            // WAFFLE-GRID
            translate([box_w/2, box_d/2, 0]) 
                intersection() {
                    hex_grid_centered(124, 96, 15.0, 1.8); 
                    translate([0, 0, 0.8]) cube([200, 200, 1.6], center=true);
                }
        }
        
        // EUROBOX LATCH
        union() {
            translate([box_w/2, 0.8, -4.75]) cube([31.0, 1.6, 15.5], center=true);
            translate([box_w/2, 2.0, -11.5]) cube([31.0, 2.4, 2.0], center=true);
            translate([box_w/2, -0.3, -3.0]) cube([31.0, 0.6, 2.0], center=true);
        }
        
        // POCKET DOOR PINS (Zapfen)
        // Y = 117.3 lokal (entspricht Y=120.0 global)
        // Z = 0.5 lokal (entspricht Z=34.5 global, exakt unter dem Dach der Führung)
        translate([6.2, 117.3, 0.5]) rotate([0, -90, 0]) cylinder(d=3.0, h=3.0, $fn=24);
        translate([box_w - 6.2, 117.3, 0.5]) rotate([0, 90, 0]) cylinder(d=3.0, h=3.0, $fn=24);
    }
}
"""
content = content.replace(old_stage_lid, new_stage_lid)


# 3. Animation Block (Drop into Pocket)
old_anim_block = re.search(r'// ANIMATION \(Pull, Drop, Hinge\).*?\s*stage_lid\(\);', content, re.DOTALL).group(0)

new_anim_block = """// ANIMATION (Pocket Door / Barrister Bookcase)
    // 1. Klappt auf (0.0 bis 0.5)
    // 2. Fällt in den Schacht (0.5 bis 1.0)
    anim_angle = ($t < 0.5) ? ($t / 0.5) * 90 : 90;
    anim_drop  = ($t >= 0.5) ? (($t - 0.5) / 0.5) * 30.5 : 0;

    translate([0, 0, 34.0 - anim_drop])
        translate([0, 120.0, 0.5])
        rotate([-anim_angle, 0, 0])
        translate([0, -120.0, -0.5])
        stage_lid();"""
content = content.replace(old_anim_block, new_anim_block)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
