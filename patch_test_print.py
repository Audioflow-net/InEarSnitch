import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# 1. Update flags
old_flags = r'show_tpu_main = .*?;\nshow_petg_chassis = .*?;\nshow_tpu_sleeve = .*?;\nshow_dummy_mic = .*?;\nshow_cross_section = .*?;\nshow_test_print = .*?;'
new_flags = """show_tpu_main = false;
show_petg_chassis = false;
show_tpu_sleeve = false;
show_dummy_mic = false;
show_cross_section = false;
show_test_print = true; // TEST-DRUCK FÜR DIE LOGO ECKE"""
content = re.sub(old_flags, new_flags, content, flags=re.DOTALL)

# 2. Update test_print module bounding box
old_test = r'translate\(\[20\.0, 50\.0, 2\.0\]\)\n\s*cube\(\[76\.0, 35\.0, 28\.0\]\);'
new_test = """// Bounding Box EXAKT für das Logo links oben:
                // X=-2 bis X=35 -> Deckt die Wand und das gesamte Logo ab
                // Y=60 bis Y=95 -> Deckt die Wand oben und den Kabelgraben ab
                translate([-2.0, 60.0, 2.0])
                    cube([37.0, 35.0, 28.0]);"""
content = re.sub(old_test, new_test, content)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
