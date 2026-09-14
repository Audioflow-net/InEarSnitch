import re

with open("V27_MASTER_COLLECTION_NEW.scad", "r") as f:
    lines = f.readlines()

out_lines = []
skip = False
for i, line in enumerate(lines):
    if "// DRUCK-LAYOUT (Entzerrt)" in line:
        skip = True
        # Skip this and the preceding `// ==` lines
        if len(out_lines) >= 2 and out_lines[-1].startswith("// ==="):
            out_lines.pop()
            out_lines.pop()
        continue
    
    if skip and line.startswith("// TEIL 3: WEITERE TPU TIPS"):
        # Stop skipping here
        out_lines.append("// ==========================================\n")
        skip = False
        
    if "// DRUCK-LAYOUT FÜR THIN LAYER CONE MOLD" in line:
        # Skip the rest of the file
        if len(out_lines) >= 2 and out_lines[-1].startswith("// ==="):
            out_lines.pop()
            out_lines.pop()
        break
        
    if not skip:
        out_lines.append(line)

# Now append the MASTER LAYOUT GRID
master_layout = """
// ==========================================
// DRUCK-LAYOUT (ORGANISIERTES RASTER)
// ==========================================

// --- REIHE 1: V27 STANDARD (13mm Zylinder) ---
translate([0, 100, 0]) color("LightGreen", 0.5) sleeve(); // Hülse (Universal für 34x34)
translate([-50, 50, 0]) color("Gray") form_left();
translate([ 50, 50, 0]) color("Silver") form_right();
translate([-20, 0, 0]) color("Orange") piston_large_7mm();
translate([ 20, 0, 0]) color("Gold") piston_small_6mm();

// --- REIHE 2: V29 THIN LAYER CONE (Upside Down) ---
translate([-50, -60, 0]) color("DarkGray") form_left_cone();
translate([ 50, -60, 0]) color("Gray") form_right_cone();
translate([  0, -110, 0]) color("Red") piston_cone_thin();

// --- REIHE 3: TPU TIPS (Optional) ---
translate([-50, -160, 0]) color("Coral") tpu_single_balloon();
translate([ 50, -160, 0]) color("SkyBlue") tpu_dual_balloon();
"""

out_lines.append(master_layout)

with open("V27_MASTER_COLLECTION.scad", "w") as f:
    f.writelines(out_lines)
