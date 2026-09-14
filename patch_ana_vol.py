import re

with open("analysis.py", "r") as f:
    code = f.read()

old_ana = """        # 1. Absolute Volume Check
        if val_1k < 75.0:
            report.append({'title': f'{channel} Capture Volume', 'status': 'WARN', 'desc': f'Measurement volume is very low ({val_1k:.1f} dB). Turn up the interface input gain for better SNR.', 'band': None})
            
        if val_50 < val_1k - 10:"""

new_ana = """        if val_50 < val_1k - 10:"""

code = code.replace(old_ana, new_ana)

with open("analysis.py", "w") as f:
    f.write(code)

print("analysis.py volume check removed.")
