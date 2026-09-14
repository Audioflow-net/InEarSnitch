import sys

with open('main.py', 'r') as f:
    content = f.read()

# Replace Tiefer/Rausziehen with unambiguous instructions
content = content.replace(
    "depth_html = \"<span style='color: #ef4444; font-weight: bold;'>Tiefer (Peak: {:.1f}kHz)</span>\".format(peak_freq/1000)",
    "depth_html = \"<span style='color: #ef4444; font-weight: bold;'>Tiefer reindrücken! (Peak: {:.1f}kHz -> Ziel: 8kHz)</span>\".format(peak_freq/1000)"
)
content = content.replace(
    "depth_html = \"<span style='color: #ef4444; font-weight: bold;'>Rausziehen (Peak: {:.1f}kHz)</span>\".format(peak_freq/1000)",
    "depth_html = \"<span style='color: #ef4444; font-weight: bold;'>Etwas rausziehen! (Peak: {:.1f}kHz -> Ziel: 8kHz)</span>\".format(peak_freq/1000)"
)
content = content.replace(
    "depth_html = \"<span style='color: #10b981; font-weight: bold;'>Tiefe: PERFEKT (8kHz)</span>\"",
    "depth_html = \"<span style='color: #10b981; font-weight: bold;'>Tiefe: PERFEKT (Resonanz bei 8kHz)</span>\""
)

with open('main.py', 'w') as f:
    f.write(content)
