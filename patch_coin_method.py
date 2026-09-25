import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# Replace the entire cutouts logo section
old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO.*?scale\(\[logo_scale, logo_scale\]\) logo_bridges_2d\(\);\n\s*\}\n\s*\}'
new_cutouts = """// 5. DAS INTEGRIERTE LOGO (DIE MÜNZ-METHODE!)
    // Ein simples kreisrundes Loch im TPU, in das die fertige PETG-Münze gepresst wird.
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        cylinder(r=12.5, h=4.0 + 2*eps, $fn=64);
"""
if re.search(old_cutouts, content, re.DOTALL):
    content = re.sub(old_cutouts, new_cutouts, content, flags=re.DOTALL)
else:
    # fallback if regex failed due to formatting
    old_cutouts_fallback = r'// 5\. DAS INTEGRIERTE LOGO.*?translate\(\[logo_x, logo_y, depth \+ flange_t - 4\.0\]\)\s*union\(\) \{.*?\n\s*\}\n'
    content = re.sub(old_cutouts_fallback, new_cutouts, content, flags=re.DOTALL)

# Replace the logo_medallion module with the two Coin options
old_medallion = r'module logo_medallion\(\) \{.*?\}'
new_medallion = """// ==========================================
// DIE MÜNZ-METHODE (PETG COIN)
// ==========================================

module petg_coin_embossed() {
    color("Silver")
    union() {
        // Basis-Münze (z.B. in Weiß oder Grau gedruckt)
        cylinder(r=12.5 - 0.1, h=3.0, $fn=64);
        
        // Erhabenes Logo (Hier im Slicer Pause setzen und auf schwarzes PETG wechseln!)
        translate([0, 0, 3.0])
            linear_extrude(height=1.0) {
                scale([logo_scale, logo_scale]) custom_logo_2d();
                scale([logo_scale, logo_scale]) waves_block();
            }
    }
}

module petg_coin_engraved() {
    color("Orange")
    difference() {
        // Massive Münze
        cylinder(r=12.5 - 0.1, h=4.0, $fn=64);
        
        // Eingraviertes Logo (Einfarbig drucken, Logo wirkt durch Schatten!)
        translate([0, 0, 3.0])
            linear_extrude(height=1.0 + eps) {
                scale([logo_scale, logo_scale]) custom_logo_2d();
                scale([logo_scale, logo_scale]) waves_block();
            }
    }
}

// =========================================="""
content = re.sub(old_medallion, new_medallion, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V32_Coin.scad', 'w') as f:
    f.write(content)
