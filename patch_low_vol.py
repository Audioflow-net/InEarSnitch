import re

with open("analysis.py", "r") as f:
    code = f.read()

old_code = """        val_1k = mag[idx_1k]
        val_50 = mag[idx_50]
        val_5k = mag[idx_5k]
        
        if val_50 < val_1k - 10:"""

new_code = """        val_1k = mag[idx_1k]
        val_50 = mag[idx_50]
        val_5k = mag[idx_5k]
        
        # 1. Absolute Volume Check
        if val_1k < 75.0:
            report.append({'title': f'{channel} Capture Volume', 'status': 'WARN', 'desc': f'Measurement volume is very low ({val_1k:.1f} dB). Turn up the interface input gain for better SNR.', 'band': None})
            
        if val_50 < val_1k - 10:"""

code = code.replace(old_code, new_code)

with open("analysis.py", "w") as f:
    f.write(code)

print("Low volume warning patched.")
