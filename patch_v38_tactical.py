import re

with open('Peli1020_TPU_Insert_V37_Pure.scad', 'r') as f:
    content = f.read()

# Add the patch_contour module near the top or before it's used
contour_module = """module patch_contour() {
    // 3mm organischer Rand um das Logo für den "Tactical Patch" Look
    offset(r=-1, $fn=32) offset(r=4, $fn=32) {
        scale([logo_scale, logo_scale]) custom_logo_2d();
    }
}
"""

# Replace the medallion
old_medallion = r'// ==========================================\n// PURE LOGO \(TESA-FILM METHOD\).*?// =========================================='
new_medallion = """// ==========================================
// TACTICAL PATCH (V38)
// ==========================================
""" + contour_module + """
module logo_medallion() {
    union() {
        // Basis-Block (z.B. in Weiß/Grau)
        color("Silver")
        linear_extrude(height=3.0) {
            offset(r=-0.1) // 0.1mm Toleranz fürs leichte Einsetzen
                patch_contour();
        }
        
        // Erhabene Details (Filament-Wechsel auf Schwarz!)
        color("Black")
        translate([0, 0, 3.0])
        linear_extrude(height=1.0) {
            scale([logo_scale, logo_scale]) custom_logo_2d();
        }
    }
}
// =========================================="""
content = re.sub(old_medallion, new_medallion, content, flags=re.DOTALL)

# Replace the cutouts
old_cutout = r'// 5\. DAS INTEGRIERTE LOGO \(PURE TESA-METHODE V36!\).*?\}\n'
new_cutout = """// 5. DAS INTEGRIERTE LOGO (TACTICAL PATCH V38!)
    // Ein massives Loch für den ganzen Block, keine filigranen Wände mehr!
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        linear_extrude(height=4.0 + 2*eps) {
            patch_contour();
        }
"""
content = re.sub(old_cutout, new_cutout, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V38_Tactical.scad', 'w') as f:
    f.write(content)
