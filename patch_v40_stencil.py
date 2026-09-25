with open('Peli1020_TPU_Insert_V39_Round.scad', 'r') as f:
    content = f.read()

# Replace logo_medallion completely
old_medallion = """module logo_medallion() {
    union() {
        // Basis-Block (z.B. in Weiß/Grau)
        color("Silver")
        linear_extrude(height=3.0) {
            offset(r=-0.1) // 0.1mm Toleranz fürs leichte Einsetzen
                patch_contour();
        }
        
        // Erhabene Details (Filament-Wechsel auf Schwarz!)
        color("Black")
        translate([0, 0, 3.0])
        linear_extrude(height=1.0) {
            scale([logo_scale, logo_scale]) custom_logo_2d();
        }
    }
}"""
new_medallion = """module logo_medallion() {
    color("LimeGreen")
    linear_extrude(height=4.0) {
        difference() {
            offset(r=-0.15) // 0.15mm Toleranz für perfekten Sitz im TPU
                patch_contour();
            scale([logo_scale, logo_scale]) custom_logo_2d();
        }
    }
}"""
content = content.replace(old_medallion, new_medallion)

with open('Peli1020_TPU_Insert_V40_Stencil.scad', 'w') as f:
    f.write(content)
