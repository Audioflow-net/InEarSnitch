import sys

with open('main.py', 'r') as f:
    content = f.read()

old_rta_depth = """                    if peak_freq < 7800:
                        depth_html = "<span style='color: #ef4444; font-weight: bold;'>Push Deeper! (Peak: {:.1f}kHz -> Target: 8kHz)</span>".format(peak_freq/1000)
                    elif peak_freq > 8200:
                        depth_html = "<span style='color: #ef4444; font-weight: bold;'>Pull Out Slightly! (Peak: {:.1f}kHz -> Target: 8kHz)</span>".format(peak_freq/1000)
                    else:
                        depth_html = "<span style='color: #10b981; font-weight: bold;'>Depth: PERFECT (Resonance at 8kHz)</span>\""""

new_rta_depth = """                    if peak_freq < 7000:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Push Deeper (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    elif peak_freq > 8600:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Pull Out Slightly (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    else:
                        depth_html = "<span style='color: #10b981; font-weight: bold;'>Depth OK ({:.1f}kHz)</span>".format(peak_freq/1000)"""

content = content.replace(old_rta_depth, new_rta_depth)

with open('main.py', 'w') as f:
    f.write(content)
