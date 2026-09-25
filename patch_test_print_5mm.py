import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# Update the Z height of the test print bounding box to only capture the top 6mm
old_test = r'translate\(\[-2\.0, 60\.0, 2\.0\]\)\n\s*cube\(\[37\.0, 35\.0, 28\.0\]\);'
new_test = """translate([-2.0, 60.0, 20.0])
                    cube([37.0, 35.0, 6.0]);"""
content = re.sub(old_test, new_test, content)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
