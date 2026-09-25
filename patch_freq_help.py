import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """        idx = self.tab_widget.currentIndex()
        if idx == 0:
            return # No help needed for Freq Response yet
        elif idx == 1:"""

new_logic = """        idx = self.tab_widget.currentIndex()
        if idx == 0:
            self.popup.setText("<b>Frequency Response</b> shows the overall tonal balance (the 'sound signature') of the In-Ear Monitor from Sub-Bass to Upper Treble.<br><br>"
                               "• <b>Sub-Bass (20 - 60 Hz):</b> Rumble and physical impact. High elevation here gives cinematic depth.<br>"
                               "• <b>Mid-Bass (60 - 250 Hz):</b> Punch, warmth, and body. Too much can make the sound 'muddy' or 'boomy'.<br>"
                               "• <b>Mids (250 - 2000 Hz):</b> Vocals and core instruments. A dip here creates a 'V-Shape', pushing vocals back.<br>"
                               "• <b>Treble (2kHz - 10kHz):</b> Clarity, attack, and presence. Sharp peaks here can cause sibilance or harshness.<br>"
                               "• <b>Air (10kHz+):</b> Sense of spaciousness and soundstage.<br><br>"
                               "<b>How to use:</b><br>"
                               "Select a Reference Target (e.g., IEF Neutral) from the dropdown below to see how your IEM deviates from a known baseline.")
        elif idx == 1:"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
