import re

with open('Peli1020_TPU_Insert_V40_Stencil.scad', 'r') as f:
    content = f.read()

# 1. Update logo_scale
content = re.sub(r'logo_scale = 1\.2;', 'logo_scale = 0.9;', content)

# 2. Update logo_x and logo_y
content = re.sub(r'logo_x = 13\.5;', 'logo_x = 13.5;', content)
content = re.sub(r'logo_y = 83\.5;', 'logo_y = 83.0;', content)

# 3. Update patch_contour to 17.5
old_contour = r'module patch_contour\(\) \{.*?circle\(d=tip_bore_d, \$fn=60\);\n\}'
new_contour = """module patch_contour() {
    // 17.5mm ist das absolute Maximum, was oben links reinpasst, ohne Wände wegzuschneiden!
    circle(d=17.5, $fn=60);
}"""
content = re.sub(old_contour, new_contour, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V41_Fit.scad', 'w') as f:
    f.write(content)
