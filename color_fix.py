import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Change colors
content = content.replace('color("#2A2D32")', 'color("#E0E0E0") // Hellgrau für Details')
content = content.replace('color("#1E2024")', 'color("#D3D3D3") // Hellgrau für Details')

# Just to be absolutely sure the global translate is gone, let's use regex
content = re.sub(r'translate\(\[-iem_bay_w/2, -iem_bay_d/2, 0\]\) \{.*?\n\}', '', content, flags=re.DOTALL)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
