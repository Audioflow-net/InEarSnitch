import re

with open('Peli1020_TPU_Insert_V34_Fusion.scad', 'r') as f:
    content = f.read()

# 1. Replace the bottom section (medallion and fused_logo_base)
old_bottom = r'// ==========================================\n// DIE EISBERG-SNAPFIT-METHODE \(TRUE FUSION V34\).*'
new_bottom = """// ==========================================
// PURE LOGO (TESA-FILM METHOD)
// ==========================================

module logo_medallion() {
    color("darkturquoise")
    // Pures, originales Logo in 4.0mm Dicke. 
    // 5 Einzelteile, perfekt für den Tesa-Film-Trick!
    linear_extrude(height=4.0) {
        scale([logo_scale, logo_scale]) custom_logo_2d();
        scale([logo_scale, logo_scale]) waves_block();
    }
}
// =========================================="""
content = re.sub(old_bottom, new_bottom, content, flags=re.DOTALL)

# 2. Replace the cutout section
old_cutout = r'// 5\. DAS INTEGRIERTE LOGO \(DIE EISBERG-SNAPFIT-METHODE V34!\).*?\}\s*\}\n'
new_cutout = """// 5. DAS INTEGRIERTE LOGO (PURE TESA-METHODE V36!)
    // Purer, sauberer 4.0mm tiefer Ausschnitt für das Original-Logo.
    // Null Toleranz-Hacks, null Brücken.
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        linear_extrude(height=4.0 + 2*eps) {
            scale([logo_scale, logo_scale]) custom_logo_2d();
            scale([logo_scale, logo_scale]) waves_block();
        }
"""
content = re.sub(old_cutout, new_cutout, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V36_Pure.scad', 'w') as f:
    f.write(content)
