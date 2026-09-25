import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

old_test = r'module test_print\(part="tpu"\) \{.*?\}'
new_test = """module test_print(part="tpu") {
    // Ultra-Micro Testdruck (ALLE WÄNDE WEG!)
    // Nur ein 23x16mm Block exakt um das Logo herum, ohne den Gehäuserand!
    translate([0, 0, -(23.62 + 1.5 - 7.0)]) {
        intersection() {
            tpu_insert_full();
            translate([2.5, 75.5, 23.62 + 1.5 - 7.0])
                cube([23.0, 16.0, 7.0]);
        }
    }
}"""
content = re.sub(old_test, new_test, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
