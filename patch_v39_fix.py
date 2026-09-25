with open('Peli1020_TPU_Insert_V38_Tactical.scad', 'r') as f:
    content = f.read()

old_contour = """module patch_contour() {
    // 3mm organischer Rand um das Logo für den "Tactical Patch" Look
    offset(r=-1, $fn=32) offset(r=4, $fn=32) {
        scale([logo_scale, logo_scale]) custom_logo_2d();
    }
}"""
new_contour = """module patch_contour() {
    // Exakt selbe Größe wie die Tip-Molds für perfekte visuelle Integration!
    circle(d=tip_bore_d, $fn=60);
}"""
content = content.replace(old_contour, new_contour)

with open('Peli1020_TPU_Insert_V39_Round.scad', 'w') as f:
    f.write(content)
