import re

with open('Peli1020_TPU_Insert_V36_Pure.scad', 'r') as f:
    content = f.read()

# Remove the waves_block() calls from the medallion
content = re.sub(r'scale\(\[logo_scale, logo_scale\]\) waves_block\(\);', '', content)

# Write to V37
with open('Peli1020_TPU_Insert_V37_Pure.scad', 'w') as f:
    f.write(content)
