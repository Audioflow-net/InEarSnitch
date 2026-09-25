import re

with open("InEarSnitch.spec", "r") as f:
    content = f.read()

old_datas = """    # App Logo
    (os.path.join(PROJECT_DIR, 'Final Logo InEar Snitch.png'), '.'),
]"""

new_datas = """    # App Logos
    (os.path.join(PROJECT_DIR, 'Final Logo InEar Snitch.png'), '.'),
    (os.path.join(PROJECT_DIR, 'Final Logo InEar Snitch_Light.png'), '.'),
    (os.path.join(PROJECT_DIR, 'Final Logo InEar Snitch_Transparent.png'), '.'),
]"""

content = content.replace(old_datas, new_datas)

with open("InEarSnitch.spec", "w") as f:
    f.write(content)
