import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# Update X coordinate to 15.65
content = content.replace('[18.15, 80.75,', '[15.65, 80.75,')

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
