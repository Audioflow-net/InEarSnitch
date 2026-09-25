import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# 1. Update Parameters (scale, x, y)
old_params = r'logo_x = 12\.0;\nlogo_y = 84\.0;'
new_params = """logo_x = 13.5;
logo_y = 83.5;
logo_scale = 1.2; // Das Logo ist jetzt 20% größer!"""
content = re.sub(old_params, new_params, content)

# 2. Update cutouts()
old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO.*?offset\(r=0\.2\) logo_tower_2d\(\);\n\s*\}'
new_cutouts = """// 5. DAS INTEGRIERTE LOGO (Top Left) - TIEFES MEDAILLON MIT TRÄGERPLATTE!
    // 4.0mm tiefe, exakte Ausstanzung für das Logo (Sichtbarer Bereich)
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        linear_extrude(height=4.0 + 2*eps) {
            offset(r=0.2) scale([logo_scale, logo_scale]) custom_logo_2d();
            offset(r=0.2) scale([logo_scale, logo_scale]) waves_block();
        }
    // 0.6mm tiefe, ovale Aussparung GANZ UNTEN für die verbindende Trägerplatte.
    // Das TPU wird beim Drucken über diese winzige 0.6mm Lücke "bridgen". 
    // Es wird minimal durchhängen, fängt sich aber sofort am massiven Boden darunter auf!
    translate([logo_x, logo_y, depth + flange_t - 4.6])
        linear_extrude(height=0.6 + eps) {
            offset(r=0.2) scale([logo_scale, logo_scale]) logo_tower_2d();
        }"""
content = re.sub(old_cutouts, new_cutouts, content, flags=re.DOTALL)

# 3. Update logo_medallion()
old_medallion = r'module logo_medallion\(\) \{.*?\}'
new_medallion = """module logo_medallion() {
    color("darkturquoise")
    union() {
        // 0.4mm dicke ovale Bodenplatte (Druckt als allererstes, verbindet alle losen Teile!)
        linear_extrude(height=0.4) scale([logo_scale, logo_scale])
            logo_tower_2d();
            
        // 4.0mm dicke Logo-Elemente darauf
        translate([0, 0, 0.4 - eps])
        linear_extrude(height=4.0 + eps) scale([logo_scale, logo_scale]) {
            custom_logo_2d();
            waves_block();
        }
    }
}"""
content = re.sub(old_medallion, new_medallion, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
