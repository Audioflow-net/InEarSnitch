import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

content = content.replace('"📊 Freq Response"', '"Freq Response"')
content = content.replace('"📉 Distortion (THD)"', '"Distortion (THD)"')
content = content.replace('"🌊 Waterfall (CSD)"', '"Waterfall (CSD)"')
content = content.replace('"🩺 Diagnostics"', '"Diagnostics"')
content = content.replace('"🎛️ Hardware EQ"', '"EQ"')
# In case the emoji doesn't have the variation selector in the string:
content = content.replace('"🎛 Hardware EQ"', '"EQ"')

with open('analysis_ui.py', 'w') as f:
    f.write(content)
