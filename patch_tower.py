import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# 1. Add logo_tower_2d module
tower_module = """
module logo_tower_2d() {
    // Ein massiver ovaler Turm (20x15mm), der das filigrane Logo trägt
    hull() {
        translate([-2.5, 0]) circle(r=7.5);
        translate([2.5, 0]) circle(r=7.5);
    }
}
"""
content = re.sub(r'(module custom_logo_2d\(\) \{.*?\})', r'\1\n' + tower_module, content, flags=re.DOTALL)

# 2. Update cutouts
old_cutout = r'// 5\. DAS INTEGRIERTE LOGO.*?offset\(r=0\.2\) custom_logo_2d\(\);'
new_cutout = """    // 5. DAS INTEGRIERTE LOGO (Top Left)
    // A) Der massive Turm-Ausschnitt (von Z=2.0 bis Z=21.12)
    translate([38.0, 79.5, 2.0 - eps])
        linear_extrude(height=19.12 + eps)
            offset(r=0.2) logo_tower_2d(); // 0.2mm Toleranz
            
    // B) Die filigranen Logo-Löcher (nur die obersten 4mm!)
    translate([38.0, 79.5, 21.12 - eps])
        linear_extrude(height=depth + flange_t - 21.12 + 2*eps)
            offset(r=0.2) custom_logo_2d();"""
content = re.sub(old_cutout, new_cutout, content, flags=re.DOTALL)

# 3. Update petg_chassis
old_chassis = r'// 3\. DIE LOGO-STELZEN.*?custom_logo_2d\(\);'
new_chassis = """            // 3. DIE LOGO-STELZEN & TURM (Top Left Corner)
            // A) Der massive Basis-Turm (Z=2.0 bis Z=21.12)
            translate([38.0, 79.5, 2.0 - eps])
                linear_extrude(height=19.12 + eps)
                    logo_tower_2d();
                    
            // B) Die filigranen Logo-Details oben drauf (Z=21.12 bis Z=25.12)
            translate([38.0, 79.5, 21.12 - eps])
                linear_extrude(height=depth + flange_t - 21.12 + eps)
                    custom_logo_2d();"""
content = re.sub(old_chassis, new_chassis, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
