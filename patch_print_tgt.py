import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_tgt = """        # Plot Target (CSV)
        if tgt_freqs is not None and tgt_mags is not None:
            interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)"""

new_tgt = """        # Plot Target (CSV)
        print("TGT FREQS", tgt_freqs is not None, "TGT MAGS", tgt_mags is not None, "FREQS", freqs is not None)
        if tgt_freqs is not None and tgt_mags is not None:
            interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)"""
content = content.replace(old_tgt, new_tgt)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
