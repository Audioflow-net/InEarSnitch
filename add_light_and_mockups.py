import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Add mock modules for Battery, LED, Pogo Pins, and Light Cone
mock_modules = """
// ==============================================================================
// MOCKUPS (Zur Visualisierung von Hardware & Licht)
// ==============================================================================
module mock_battery() {
    color("#FF3333") rounded_pocket(50, 15, 32, r=2);
}

module mock_pogo_pin() {
    color("#FFD700") {
        cylinder(d=2.5, h=10, $fn=16);
        translate([0,0,10]) cylinder(d1=2.5, d2=0.5, h=2, $fn=16);
    }
}

module mock_led_stripe() {
    color("#FFFF00") cube([50, 8, 1.5], center=true);
}

module light_cone() {
    color([1.0, 0.9, 0.0, 0.2]) // Transparent Yellow
        translate([0, 0, 0])
        rotate([90, 0, 0])
        cylinder(d1=8, d2=120, h=100, $fn=30);
}
"""
content = content.replace("// ==============================================================================\n// HILFS-MODULE", mock_modules + "\n// ==============================================================================\n// HILFS-MODULE")

# 2. Add them to the Assembly (!layout_mode)
assembly_additions = """
    for (c = [0 : cols - 1]) {
        bay_x = wall + c * (iem_bay_w + wall);
        bay_y = wall;
        translate([bay_x + 3, bay_y + 3, floor_h + silica_vault_h - 1.6])
            silica_grid_cover();
        translate([bay_x, bay_y, floor_h + silica_vault_h])
            tpu_iem_tray_v9();
    }
    
    // VISUALISIERUNG: Akku (Shure SB900 oder 2xAA) in der Power Bay (c=1)
    translate([wall + iem_bay_w + wall + 10, wall + iem_bay_d + wall + 0.5, 2.4])
        mock_battery();
        
    // VISUALISIERUNG: Pogo-Pins in der Base
    slot_y = box_d - wall - 3.6;
    translate([box_w/2 - 20, slot_y + 1.8, 1.0]) mock_pogo_pin();
    translate([box_w/2 + 20, slot_y + 1.8, 1.0]) mock_pogo_pin();
"""
content = re.sub(r'    for \(c = \[0 : cols - 1\]\) \{.*?tpu_iem_tray_v9\(\);\n    \}', assembly_additions, content, flags=re.DOTALL)

# 3. Modify the Lid: Add the Angled "Licht-Schaufel" (Brow) and remove the flat LED pocket
old_lid = re.search(r'module stage_lid\(\) \{.*?(?=\n// ==============================================================================\n// TPU INLAYS)', content, re.DOTALL).group(0)

new_lid = """module stage_lid() {
    lid_w = box_w - 5.4;
    lid_d = box_d - 5.4;
    
    color("#B0B0B0")
    union() {
        difference() {
            union() {
                translate([2.7, 2.7, 0]) rounded_pocket(lid_w, lid_d, lid_h, r=1.8);
                
                // NEU: Die Licht-Schaufel (Angled Brow)
                // Ragt im geschlossenen Zustand nach UNTEN in die Box.
                // Im offenen (vertikalen) Zustand ragt sie nach VORNE und richtet das Licht im 45° Winkel nach unten!
                translate([box_w/2 - 28, 2.7, -6]) 
                    rounded_pocket(56, 12, 6, r=2);
            }
                
            // Label auf der OBERSEITE
            translate([box_w/2 - 30, 15, lid_h - 0.6]) cube([60, 15, 0.7]);
                
            // Whiteboard / Cheat-Sheet auf der INNENSEITE
            translate([15, 16, -0.1]) rounded_pocket(lid_w - 30, lid_d - 50, 0.6, r=2);
                
            // MAGIC CONTACT SYSTEM (Kupfer-Nuten)
            translate([box_w/2 - 20, 14, -0.1]) cube([6, lid_d, 0.4]);
            translate([box_w/2 + 14, 14, -0.1]) cube([6, lid_d, 0.4]);
                
            // NEU: Abgewinkelte LED-Mulde in der Licht-Schaufel (45 Grad geneigt!)
            translate([box_w/2, 10, -3])
                rotate([-45, 0, 0])
                cube([52, 12, 4], center=true);
        }
        
        // Airtight Pull-Tab
        translate([box_w/2 - 15, 0.5, 0]) rounded_pocket(30, 4, lid_h, r=1);
        
        // Die Scharnier-Pins (1.9mm lang)
        translate([1.75, lid_d - 1.8, 1.5]) rotate([0, 90, 0]) cylinder(d=2.8, h=1.9, center=true, $fn=16);
        translate([145.45, lid_d - 1.8, 1.5]) rotate([0, 90, 0]) cylinder(d=2.8, h=1.9, center=true, $fn=16);
            
        // Schnapp-Nasen (Snap-Fit)
        translate([box_w/2 - 30, 2.7, 1.5]) sphere(d=1.5, $fn=16);
        translate([box_w/2 + 30, 2.7, 1.5]) sphere(d=1.5, $fn=16);
        
        // VISUALISIERUNG: LED Stripe + Lichtkegel (nur sichtbar im gerenderten Deckel)
        if (!layout_mode) {
            translate([box_w/2, 10.5, -2.5])
                rotate([-45, 0, 0]) {
                    mock_led_stripe();
                    translate([0, 0, -2]) light_cone();
                }
        } else {
             translate([box_w/2, 10.5, -2.5])
                rotate([-45, 0, 0]) mock_led_stripe();
        }
    }
}"""

content = content.replace(old_lid, new_lid)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
