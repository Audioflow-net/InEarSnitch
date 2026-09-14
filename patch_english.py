import sys

with open('main.py', 'r') as f:
    content = f.read()

content = content.replace("IEM nicht erkannt (Stille)", "IEM Not Detected (Silence)")
content = content.replace("Tiefer reindrücken! (Peak: {:.1f}kHz -> Ziel: 8kHz)", "Push Deeper! (Peak: {:.1f}kHz -> Target: 8kHz)")
content = content.replace("Etwas rausziehen! (Peak: {:.1f}kHz -> Ziel: 8kHz)", "Pull Out Slightly! (Peak: {:.1f}kHz -> Target: 8kHz)")
content = content.replace("Tiefe: PERFEKT (Resonanz bei 8kHz)", "Depth: PERFECT (Resonance at 8kHz)")

with open('main.py', 'w') as f:
    f.write(content)
