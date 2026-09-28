with open('analysis_ui.py', 'r') as f:
    content = f.read()

target = """            snr_l = getattr(self, '_snr_l', None)
            snr_r = getattr(self, '_snr_r', None)
            
            if thd_l is not None:
                is_poor_snr_l = (snr_l is not None and snr_l < 75.0)"""

replacement = """            snr_l = getattr(self, '_snr_l', None)
            snr_r = getattr(self, '_snr_r', None)
            
            is_poor_snr_l = (snr_l is not None and snr_l < 75.0)
            is_poor_snr_r = (snr_r is not None and snr_r < 75.0)
            
            if thd_l is not None:"""

content = content.replace(target, replacement)

target2 = """            if thd_r is not None:
                is_poor_snr_r = (snr_r is not None and snr_r < 75.0)"""

replacement2 = """            if thd_r is not None:"""

content = content.replace(target2, replacement2)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("Fixed UnboundLocalError!")
