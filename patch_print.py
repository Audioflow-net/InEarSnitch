import re
with open('analysis_ui.py', 'r') as f:
    content = f.read()

content = content.replace("if tgt_freqs is not None and tgt_mags is not None:", 
                          "print('DEBUG: tgt_freqs=', type(tgt_freqs), 'tgt_mags=', type(tgt_mags))\n            if tgt_freqs is not None and tgt_mags is not None:")

with open('analysis_ui.py', 'w') as f:
    f.write(content)
