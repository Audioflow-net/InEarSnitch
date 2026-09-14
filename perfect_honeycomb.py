import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Replace the old hex_grid with hex_grid_centered
old_hex_module = re.search(r'module hex_grid\(w, d, d_hex, wall\) \{.*?(?=\nmodule rounded_pocket)', content, re.DOTALL).group(0)

new_hex_module = """module hex_grid_centered(w, d, d_hex, wall) {
    dx = d_hex + wall;
    dy = dx * sin(60);
    cols = ceil(w / dx / 2) + 1;
    rows = ceil(d / dy / 2) + 1;
    
    intersection() {
        cube([w, d, 50], center=true);
        for (x = [-cols : 1 : cols]) {
            for (y = [-rows : 1 : rows]) {
                offset_x = (abs(y) % 2 == 1) ? dx/2 : 0;
                translate([x * dx + offset_x, y * dy, 25]) 
                    cylinder(d=d_hex, h=60, center=true, $fn=6);
            }
        }
    }
}"""
content = content.replace(old_hex_module, new_hex_module)

# 2. Update TPU Tray Honeycomb Cutout
old_tpu_cutout = re.search(r'// Modernes Honeycomb-Gitter als Boden\n            translate\(\[2, 2, -10\]\)\n                intersection\(\) \{.*?\n                \}', content, re.DOTALL).group(0)

new_tpu_cutout = """// Modernes Honeycomb-Gitter (Perfekt zentriert!)
            intersection() {
                translate([2, 2, -10]) rounded_pocket(iem_bay_w - 4, iem_bay_d - 4, 20, r=4);
                // 5.5mm Waben, 1.5mm Stege - Exakt am Inlay-Zentrum ausgerichtet
                translate([iem_bay_w/2, iem_bay_d/2, -10]) hex_grid_centered(iem_bay_w, iem_bay_d, 5.5, 1.5);
            }"""
content = content.replace(old_tpu_cutout, new_tpu_cutout)

# 3. Update Silica Grille Honeycomb Cutout
old_silica_cutout = re.search(r'// Modernes Honeycomb-Gitter\n            translate\(\[1, 1, -10\]\)\n                intersection\(\) \{.*?\n                \}', content, re.DOTALL).group(0)

new_silica_cutout = """// Modernes Honeycomb-Gitter (Perfekt zentriert!)
            intersection() {
                translate([1.5, 1.5, -10]) rounded_pocket(grid_w - 3, grid_d - 3, 20, r=2);
                // 5.5mm Waben, 1.5mm Stege - Exakt am Gitter-Zentrum ausgerichtet
                translate([grid_w/2, grid_d/2, -10]) hex_grid_centered(grid_w, grid_d, 5.5, 1.5);
            }"""
content = content.replace(old_silica_cutout, new_silica_cutout)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
