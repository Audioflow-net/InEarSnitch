import re

with open('Peli1020_TPU_Insert_V33_Iceberg.scad', 'r') as f:
    content = f.read()

old_medallion = r'// ==========================================\n// DIE EISBERG-SNAPFIT-METHODE \(PETG\).*?// =========================================='
new_medallion = """// ==========================================
// DIE EISBERG-SNAPFIT-METHODE (TRUE FUSION V34)
// ==========================================

module fused_logo_base() {
    // 6mm aufblasen schluckt JEDE Lücke. 4mm schrumpfen bringt es auf +2mm.
    // Resultat: 100% garantiert EIN EINZIGER solider Block ohne innere Löcher!
    offset(r=-4.0, $fn=16) offset(r=6.0, $fn=16) {
        scale([logo_scale, logo_scale]) custom_logo_2d();
        scale([logo_scale, logo_scale]) waves_block();
    }
}

module logo_medallion() {
    color("darkturquoise")
    union() {
        // Die 1.0mm dicke Basisplatte (100% massiver Block)
        linear_extrude(height=1.0)
            offset(r=-0.15, $fn=16) // Toleranz
            fused_logo_base();
            
        // Die sauberen Inseln
        translate([0, 0, 1.0])
        linear_extrude(height=3.0) {
            scale([logo_scale, logo_scale]) custom_logo_2d();
            scale([logo_scale, logo_scale]) waves_block();
        }
    }
}
// =========================================="""
content = re.sub(old_medallion, new_medallion, content, flags=re.DOTALL)

old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO.*?translate\(\[0, 0, 1\.0\]\)\s*linear_extrude\(height=3\.0 \+ 2\*eps\) \{\s*scale\(\[logo_scale, logo_scale\]\) custom_logo_2d\(\);\s*scale\(\[logo_scale, logo_scale\]\) waves_block\(\);\s*\}\s*\}\n'
new_cutouts = """// 5. DAS INTEGRIERTE LOGO (DIE EISBERG-SNAPFIT-METHODE V34!)
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        union() {
            // Die "Wurzel" (Untergrund-Basis)
            linear_extrude(height=1.0 + eps)
                fused_logo_base();
            
            // Die sichtbaren, perfekten Inseln
            translate([0, 0, 1.0])
            linear_extrude(height=3.0 + 2*eps) {
                scale([logo_scale, logo_scale]) custom_logo_2d();
                scale([logo_scale, logo_scale]) waves_block();
            }
        }
"""
content = re.sub(old_cutouts, new_cutouts, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V34_Fusion.scad', 'w') as f:
    f.write(content)
