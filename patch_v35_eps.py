import re

with open('Peli1020_TPU_Insert_V34_Fusion.scad', 'r') as f:
    content = f.read()

old_medallion = r'linear_extrude\(height=1\.0\)\s*offset\(r=-0\.15, \$fn=16\) // Toleranz\s*fused_logo_base\(\);\s*// Die sauberen Inseln\s*translate\(\[0, 0, 1\.0\]\)\s*linear_extrude\(height=3\.0\)'
new_medallion = """linear_extrude(height=1.0 + 0.01) // 0.01mm OVERLAP TO PREVENT FLOATING POINT HOLES!
            offset(r=-0.15, $fn=16) // Toleranz
            fused_logo_base();
            
        // Die sauberen Inseln
        translate([0, 0, 1.0])
        linear_extrude(height=3.0)"""
        
content = re.sub(old_medallion, new_medallion, content)

with open('Peli1020_TPU_Insert_V35_Fusion_Clean.scad', 'w') as f:
    f.write(content)
