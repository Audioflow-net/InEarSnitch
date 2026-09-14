import os

filepath = '/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad'
with open(filepath, 'r') as f:
    text = f.read()

old_main_trench = """    // 2. MIDDLE BAND: THE MASSIVE CABLE TRENCH
    // Extrem weiche Kanten: 8mm seitlicher Radius und 6mm Boden-Radius (Wanne).
    // Balkone wurden entfernt für einen sauberen, aufgeräumten Look!
    translate([15.65, 28.65, depth + flange_t - cable_well_depth])
        rounded_pocket(80.0, 24.0, cable_well_depth + eps, 8, 6, 2.0);"""

new_main_trench = """    // 2. MIDDLE BAND: THE MASSIVE CABLE TRENCH
    // Extrem weiche Kanten: 8mm seitlicher Radius und 6mm Boden-Radius (Wanne).
    // Balkone (Kabel-Halter) sind wieder installiert wie in V95!
    difference() {
        translate([15.65, 28.65, depth + flange_t - cable_well_depth])
            rounded_pocket(80.0, 24.0, cable_well_depth + eps, 8, 6, 2.0);
            
        // Support-freie, angeschrägte Balkone (Tiefes Reinragen: 6mm Überhang!)
        // Vorne (ragen nach +Y)
        translate([30.0, 28.65, depth + flange_t]) wedge_tab(12.0, 6.0);
        translate([55.0, 28.65, depth + flange_t]) wedge_tab(12.0, 6.0);
        translate([80.0, 28.65, depth + flange_t]) wedge_tab(12.0, 6.0);
        // Hinten (ragen nach -Y, daher rotiert)
        translate([30.0, 28.65 + 24.0, depth + flange_t]) rotate([0, 0, 180]) wedge_tab(12.0, 6.0);
        translate([55.0, 28.65 + 24.0, depth + flange_t]) rotate([0, 0, 180]) wedge_tab(12.0, 6.0);
        translate([80.0, 28.65 + 24.0, depth + flange_t]) rotate([0, 0, 180]) rotate([0, 0, 180]) wedge_tab(12.0, 6.0); // Wait, one rotate is enough
    }"""
# Fix the double rotate in string
new_main_trench = new_main_trench.replace("rotate([0, 0, 180]) rotate([0, 0, 180])", "rotate([0, 0, 180])")

if old_main_trench in text:
    text = text.replace(old_main_trench, new_main_trench)
    with open(filepath, 'w') as f:
        f.write(text)
    print("Balconies added back successfully!")
else:
    print("Could not find the target text to replace.")

