import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Add the variable at the top
old_header = """// Basis-Dimensionen"""
new_header = """// ==============================================================================
// ANSICHTS-MODUS (TRUE = Bauteile aufgereiht, FALSE = Zusammengebaut/Animation)
layout_mode = true; 
// ==============================================================================

// Basis-Dimensionen"""
content = content.replace(old_header, new_header)

# Find the main assembly block
assembly_regex = r'(t_open = max.*?)(?=\n// ==============================================================================\n// HILFS-MODULE)'
assembly_match = re.search(assembly_regex, content, re.DOTALL)

if assembly_match:
    old_assembly = assembly_match.group(1)
    
    new_assembly = """t_open = max(0, min($t * 2, 1.0)); 
phase1 = min(t_open * 2, 1.0);       
phase2 = max(0, (t_open - 0.5) * 2); 

if (!layout_mode) {
    // ZUSAMMENGEBAUTER MODUS (ANIMATION)
    pin_y = 131.2;
    pin_z = 34.5;
    drop_z = -phase2 * (34.5 - 5.0); 

    base_case();

    translate([0, 0, drop_z])
        translate([0, pin_y, pin_z])
        rotate([phase1 * -90, 0, 0])
        translate([0, -pin_y, -pin_z])
        translate([0, 0, base_h - 4])
        stage_lid();

    for (c = [0 : cols - 1]) {
        bay_x = wall + c * (iem_bay_w + wall);
        bay_y = wall;
        translate([bay_x + 3, bay_y + 3, floor_h + silica_vault_h - 1.6])
            silica_grid_cover();
        translate([bay_x, bay_y, floor_h + silica_vault_h])
            tpu_iem_tray_v9();
    }
} else {
    // BAUTEIL-ÜBERSICHT (EXPLOSIONS-ANSICHT)
    // 1. Basis-Koffer
    base_case();
    
    // 2. Deckel (Neben dem Koffer)
    translate([0, box_d + 20, 0])
        stage_lid();
        
    // 3. TPU-Inlays (Rechts daneben)
    translate([box_w + 20, 0, 0]) tpu_iem_tray_v9();
    translate([box_w + 20, iem_bay_d + 10, 0]) tpu_iem_tray_v9();
    
    // 4. Silica-Gitter (Ganz rechts)
    translate([box_w + 20 + iem_bay_w + 20, 0, 0]) silica_grid_cover();
    translate([box_w + 20 + iem_bay_w + 20, iem_bay_d + 10, 0]) silica_grid_cover();
}
"""
    content = content.replace(old_assembly, new_assembly)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
