import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Replace the stretch to spread out the knobs
old_layout = """            bl.addStretch()
            
            # Knobs
            knob_f = FloatKnob("FREQ", 20, 20000, [60, 250, 1000, 4000, 8000][i], 'log', 'Hz')
            knob_g = FloatKnob("GAIN", -24, 24, 0, 'linear', 'dB')
            knob_q = FloatKnob("Q", 0.1, 10, 0.7 if i==0 or i==4 else 1.41, 'log', '')
            
            bl.addWidget(knob_f)
            bl.addWidget(knob_g)
            bl.addWidget(knob_q)"""

new_layout = """            # Space them evenly
            bl.addStretch()
            
            # Knobs
            knob_f = FloatKnob("FREQ", 20, 20000, [60, 250, 1000, 4000, 8000][i], 'log', 'Hz')
            knob_g = FloatKnob("GAIN", -24, 24, 0, 'linear', 'dB')
            knob_q = FloatKnob("Q", 0.1, 10, 0.7 if i==0 or i==4 else 1.41, 'log', '')
            
            bl.addWidget(knob_f)
            bl.addStretch()
            bl.addWidget(knob_g)
            bl.addStretch()
            bl.addWidget(knob_q)
            bl.addStretch()"""

content = content.replace(old_layout, new_layout)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
