import re

with open('Peli1020_TPU_Insert_V38_Tactical.scad', 'r') as f:
    content = f.read()

# Replace patch_contour
old_contour = r'module patch_contour\(\) \{.*?\}'
new_contour = """module patch_contour() {
    // Exakt selbe Größe wie die Tip-Molds für perfekte visuelle Integration!
    circle(d=tip_bore_d, $fn=60);
}"""
content = re.sub(old_contour, new_contour, content, flags=re.DOTALL)

# Since patch_contour is now a centered circle, we need to make sure the logo is centered INSIDE it.
# Wait, custom_logo_2d has its own translation: translate([-9.42, -6.21]) which centers it around [0,0].
# But wait, in the tactical patch I just offset the logo. So it was perfectly aligned.
# Now that it's a fixed circle, is the logo exactly centered?
# Yes, because custom_logo_2d() is centered at 0,0! Let's verify custom_logo_2d().
# But wait, if I replace patch_contour, the medallion translates the logo to [0,0,3.0]. The base is at [0,0,0].
# The whole medallion is then translated by [logo_x, logo_y] in cutouts().
# Let's check cutouts: translate([logo_x, logo_y, ...]) patch_contour();
# Yes, the base will be placed exactly at logo_x, logo_y!

with open('Peli1020_TPU_Insert_V39_Round.scad', 'w') as f:
    f.write(content)
