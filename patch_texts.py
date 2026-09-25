import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# THD text replacement
thd_old = r'self\.thd_help_lbl = QLabel\("<b>THD.*?Lower is better\."\)'
thd_new = """self.thd_help_lbl = QLabel("<b>Total Harmonic Distortion (THD)</b> measures how much the In-Ear Monitor alters the original audio signal by adding unwanted harmonic frequencies.<br><br>"
                                  "• <b>L2 (2nd Harmonic):</b> Sounds warm and musical. A slight elevation here is often perceived as 'thick' or 'pleasant', but too much muddies the bass.<br>"
                                  "• <b>L3 (3rd Harmonic):</b> Sounds harsh, metallic, and fatiguing. High L3 often points to mechanical issues, driver clipping, or acoustic blockages.<br><br>"
                                  "<b>What to look for:</b><br>"
                                  "A clean IEM should have THD well below 1% across most of the frequency range. Sharp, isolated spikes in the graph strongly indicate resonance issues or a failing driver.")
        self.thd_help_lbl.setMinimumWidth(700)"""
content = re.sub(thd_old, thd_new, content, flags=re.DOTALL)


# CSD text replacement
csd_old = r'self\.csd_help_lbl = QLabel\("<b>CSD.*?Less ringing is better\."\)'
csd_new = """self.csd_help_lbl = QLabel("<b>Cumulative Spectral Decay (CSD / Waterfall)</b> visualizes how quickly the In-Ear Monitor stops producing sound after the signal stops, adding the dimension of <i>Time</i> to the frequency response.<br><br>"
                                  "• <b>Clean Decay:</b> The graph drops off sharply and smoothly. This means the driver is fast and well-controlled, leading to precise transients and clear separation.<br>"
                                  "• <b>Ringing / Ridges:</b> Mountains stretching forward in time mean the driver or acoustic chamber continues to resonate. Severe ringing causes listening fatigue and smeared details.<br><br>"
                                  "<b>What to look for:</b><br>"
                                  "Focus on the lower treble (4kHz - 8kHz). A deep, fast drop-off here is the hallmark of a high-end, well-tuned IEM. Prolonged ridges indicate poor acoustic damping.")
        self.csd_help_lbl.setMinimumWidth(700)"""
content = re.sub(csd_old, csd_new, content, flags=re.DOTALL)

with open("analysis_ui.py", "w") as f:
    f.write(content)
