import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO.*?scale\(\[logo_scale, logo_scale\]\) logo_bridges_2d\(\);\n\s*\}\n'
new_cutouts = """// 5. DAS INTEGRIERTE LOGO (DIE EISBERG-SNAPFIT-METHODE!)
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        union() {
            // Die "Wurzel" (Untergrund-Basis), die alle Inseln unsichtbar verbindet.
            // TPU dehnt sich, PETG flutscht rein und TPU schnappt drüber zu (Undercut).
            linear_extrude(height=1.0 + eps)
                offset(r=2.5, $fn=16) {
                    scale([logo_scale, logo_scale]) custom_logo_2d();
                    scale([logo_scale, logo_scale]) waves_block();
                }
            
            // Die sichtbaren, perfekten Inseln (ohne hässliche Brücken!)
            translate([0, 0, 1.0])
            linear_extrude(height=3.0 + 2*eps) {
                scale([logo_scale, logo_scale]) custom_logo_2d();
                scale([logo_scale, logo_scale]) waves_block();
            }
        }
"""
if re.search(old_cutouts, content, re.DOTALL):
    content = re.sub(old_cutouts, new_cutouts, content, flags=re.DOTALL)
else:
    old_cutouts_fallback = r'// 5\. DAS INTEGRIERTE LOGO \(DIE MÜNZ-METHODE!\).*?cylinder\(r=12\.5, h=4\.0 \+ 2\*eps, \$fn=64\);'
    content = re.sub(old_cutouts_fallback, new_cutouts, content, flags=re.DOTALL)

old_medallion = r'// DIE MÜNZ-METHODE \(PETG COIN\).*?// =========================================='
new_medallion = """// ==========================================
// DIE EISBERG-SNAPFIT-METHODE (PETG)
// ==========================================

module logo_medallion() {
    color("darkturquoise")
    union() {
        // Die 1.0mm dicke Basisplatte (verbindet alle Inseln unsichtbar!)
        linear_extrude(height=1.0)
            offset(r=2.5 - 0.15, $fn=16) { // 0.15mm Toleranz fürs leichte Reindrücken
                scale([logo_scale, logo_scale]) custom_logo_2d();
                scale([logo_scale, logo_scale]) waves_block();
            }
            
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

with open('Peli1020_TPU_Insert_V33_Iceberg.scad', 'w') as f:
    f.write(content)
