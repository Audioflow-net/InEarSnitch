import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Segmented Control CSS
old_seg_css = r'''                QPushButton:checked \{\{
                    background-color: #0ea5e9;
                    color: white;
                    border-color: #0ea5e9;
                \}\}'''

new_seg_css = r'''                QPushButton:checked {{
                    background-color: #444;
                    color: white;
                    border-color: #666;
                }}'''

code = re.sub(old_seg_css, new_seg_css, code)

# 2. Save Button CSS
old_save_css = r'QPushButton \{ background-color: #0ea5e9; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: none; \} QPushButton:disabled \{ background-color: #0369a1; color: #7dd3fc; \} QPushButton:hover \{ background-color: #0284c7; \}'

new_save_css = r'QPushButton { background-color: #444; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #555; } QPushButton:disabled { background-color: #222; color: #555; border: 1px solid #333; } QPushButton:hover { background-color: #555; }'

code = code.replace(old_save_css, new_save_css)

with open("main.py", "w") as f:
    f.write(code)

print("Blue removed.")
