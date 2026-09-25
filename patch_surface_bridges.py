import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# 1. Add logo_bridges_2d() before logo_medallion()
bridges_code = """
module logo_bridges_2d() {
    // Verbindungsstege auf der Oberfläche, damit das PETG ein durchgehendes Teil ist!
    hull() {
        translate([-0.2, 0.3]) circle(r=0.25, $fn=16);
        translate([1.2, 0.6]) circle(r=0.25, $fn=16);
    }
    hull() {
        translate([-4.2, 1.2]) circle(r=0.25, $fn=16);
        translate([-2.5, 2.3]) circle(r=0.25, $fn=16);
    }
}
"""
if 'module logo_bridges_2d()' not in content:
    content = content.replace('module logo_medallion()', bridges_code + '\nmodule logo_medallion()')

# 2. Update cutouts() to use the bridges and remove the oval gap!
old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO.*?offset\(r=0\.2\) scale\(\[logo_scale, logo_scale\]\) waves_block\(\);\n\s*\}'
if old_cutouts not in content: # maybe offset was already removed
    old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO.*?scale\(\[logo_scale, logo_scale\]\) waves_block\(\);\n\s*\}'

new_cutouts = """// 5. DAS INTEGRIERTE LOGO (Top Left) - OBERFLÄCHEN-VERBUND!
    // Exakt 4.0mm tiefe Ausstanzung (Logo + Wellen + Verbindungsbrücken).
    // Kein offset(), keine Toleranz, sitzt 1:1 stramm im weichen Gummi!
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        linear_extrude(height=4.0 + 2*eps) {
            scale([logo_scale, logo_scale]) custom_logo_2d();
            scale([logo_scale, logo_scale]) waves_block();
            scale([logo_scale, logo_scale]) logo_bridges_2d();
        }"""
content = re.sub(old_cutouts, new_cutouts, content, flags=re.DOTALL)

# 3. Update logo_medallion() to remove baseplate and add bridges
old_medallion = r'module logo_medallion\(\) \{.*?\}'
new_medallion = """module logo_medallion() {
    color("darkturquoise")
    // 4.0mm dickes, massives Logo (alles durch Brücken verbunden!)
    linear_extrude(height=4.0) {
        scale([logo_scale, logo_scale]) custom_logo_2d();
        scale([logo_scale, logo_scale]) waves_block();
        scale([logo_scale, logo_scale]) logo_bridges_2d();
    }
}"""
content = re.sub(old_medallion, new_medallion, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
