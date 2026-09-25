import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """        elif idx == 1:
            self.popup.setText("<b>Total Harmonic Distortion (THD)</b> measures how much the In-Ear Monitor alters the original audio signal by adding unwanted harmonic frequencies.<br><br>"
                               "• <b>L2 (2nd Harmonic):</b> Sounds warm and musical. A slight elevation here is often perceived as 'thick' or 'pleasant', but too much muddies the bass.<br>"
                               "• <b>L3 (3rd Harmonic):</b> Sounds harsh, metallic, and fatiguing. High L3 often points to mechanical issues, driver clipping, or acoustic blockages.<br><br>"
                               "<b>What to look for:</b><br>"
                               "A clean IEM should have THD well below 1% across most of the frequency range. Sharp, isolated spikes in the graph strongly indicate resonance issues or a failing driver.")
        elif idx == 2:"""

new_logic = """        elif idx == 1:
            self.popup.setText("<b>Total Harmonic Distortion (THD)</b> measures how much the In-Ear Monitor alters the original audio signal by adding unwanted harmonic frequencies.<br><br>"
                               "• <b>L2 (2nd Harmonic):</b> Sounds warm and musical. A slight elevation here is often perceived as 'thick' or 'pleasant', but too much muddies the bass.<br>"
                               "• <b>L3 (3rd Harmonic):</b> Sounds harsh, metallic, and fatiguing. High L3 often points to mechanical issues, driver clipping, or acoustic blockages.<br><br>"
                               "<b>Stress Test (Rub & Buzz):</b><br>"
                               "Runs a high-level sweep to detect mechanical defects (like a rubbing voice coil). If the red HOHD (High Order) line spikes, the driver is likely physically damaged.<br><br>"
                               "<b>What to look for:</b><br>"
                               "A clean IEM should have THD well below 1%. Sharp, isolated spikes strongly indicate resonance issues or a failing driver.")
        elif idx == 2:"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
