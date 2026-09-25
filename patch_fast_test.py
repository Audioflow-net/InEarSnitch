import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

old_test = r'module test_print\(part="tpu"\) \{.*?\}'
new_test = """module test_print(part="tpu") {
    // Ultra-minimaler Testdruck (Ohne die dicken Gehäusewände)
    // Nur ein 28x20mm Block exakt um das Logo herum!
    translate([0, 0, -(23.62 + 1.5 - 7.0)]) {
        intersection() {
            tpu_insert_full();
            translate([logo_x - 14.0, logo_y - 10.0, 23.62 + 1.5 - 7.0])
                cube([28.0, 20.0, 7.0]);
        }
    }
}"""
content = re.sub(old_test, new_test, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
