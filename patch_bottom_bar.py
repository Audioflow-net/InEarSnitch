import re

with open("/Users/ben/Desktop/InEarSnitch/main.py", "r") as f:
    text = f.read()

# 1. We need to extract the block that adds MODULE 1, MODULE 2, MODULE 3
# and reorder them.

pattern = re.compile(r'(# --- MODULE 1: CHANNEL ---.*?)(# Separator.*?)(# --- MODULE 2: SWEEPS ---.*?)(add_sep\(\).*?)(# --- MODULE 3: PROFILES \(Target & History\) ---.*?)(control_layout\.addStretch\(\) # Push everything below to the right!)', re.DOTALL)

match = pattern.search(text)
if not match:
    print("Pattern not found!")
    exit(1)

mod_chan = match.group(1)
sep1 = match.group(2)
mod_sweeps = match.group(3)
sep2 = match.group(4)
mod_prof = match.group(5)
stretch = match.group(6)

# Swap mod_sweeps and mod_prof
new_layout = f"{mod_chan}{sep1}{mod_prof}{sep2}{mod_sweeps}        {stretch}"

# Now we need to make the btn_l and btn_r larger and specifically styled.
# We will inject a custom setStyleSheet for them right after they are created.

btn_style_l = 'btn_l.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-left-radius: 6px; border-bottom-left-radius: 6px; border-right: none; padding: 12px 24px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #16a34a; color: white; border-color: #16a34a; }")'
btn_style_r = 'btn_r.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-right-radius: 6px; border-bottom-right-radius: 6px; padding: 12px 24px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #dc2626; color: white; border-color: #dc2626; }")'

# Inject these after btn_r = ...
new_layout = new_layout.replace('btn_r = create_seg_btn("Right", "right", checked_bg="#dc2626")', f'btn_r = create_seg_btn("Right", "right", checked_bg="#dc2626")\n        {btn_style_l}\n        {btn_style_r}')

text = text[:match.start()] + new_layout + text[match.end():]

with open("/Users/ben/Desktop/InEarSnitch/main.py", "w") as f:
    f.write(text)

print("Bottom bar patched successfully.")
