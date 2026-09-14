import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# 1. M30 Male Gewinde (Auf der Basis)
old_m30_male = 'if ($preview) cylinder(d=29.6, h=5);\n            else { cylinder(d=29.6, h=5); Bulletproof_Thread(d=30, pitch=1.5, turns=3.3); }'
new_m30_male = 'if ($preview) cylinder(d=29.6, h=5);\n            else { cylinder(d=29.2, h=5); Bulletproof_Thread(d=28.8, pitch=1.5, turns=3.3); } // Max outer D = 30.0'
content = content.replace(old_m30_male, new_m30_male)

# 2. M22 Female Gewinde (In der Basis für das Mikrofon)
old_m22_female = 'if ($preview) translate([0, 0, -10]) cylinder(d=23, h=8);\n        else { translate([0, 0, -10]) cylinder(d=22.6, h=8); translate([0,0,-10]) Bulletproof_Thread(d=23, pitch=0.5, turns=16); }'
new_m22_female = 'if ($preview) translate([0, 0, -10]) cylinder(d=22.3, h=8);\n        else { translate([0, 0, -10]) cylinder(d=21.8, h=8); translate([0,0,-10]) Bulletproof_Thread(d=22.4, pitch=0.5, turns=16); } // Perfekter M22x0.5 Fit'
content = content.replace(old_m22_female, new_m22_female)

# 3. M30 Female Gewinde (In der goldenen Mutter)
old_m30_female = 'if ($preview) cylinder(d=30, h=6);\n            else { cylinder(d=29.6, h=6); Bulletproof_Thread(d=30.6, pitch=1.5, turns=4); }'
new_m30_female = 'if ($preview) cylinder(d=30, h=6);\n            else { cylinder(d=30.2, h=6); Bulletproof_Thread(d=30.8, pitch=1.5, turns=4); } // Perfekter M30x1.5 Fit mit 0.4mm Clearance'
content = content.replace(old_m30_female, new_m30_female)

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
