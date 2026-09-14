import sys

with open('analysis.py', 'r') as f:
    content = f.read()

old_thd = """        if len(idx_mid) > 0:
            avg_thd_mid = np.mean(thd_percentage[idx_mid])
            max_thd_mid = np.max(thd_percentage[idx_mid])"""

new_thd = """        if len(idx_mid) > 0:
            avg_thd_mid = np.clip(np.mean(thd_percentage[idx_mid]), 0, 100)
            max_thd_mid = np.clip(np.max(thd_percentage[idx_mid]), 0, 100)"""
content = content.replace(old_thd, new_thd)

old_bass = """        if len(idx_bass) > 0:
            avg_thd_bass = np.mean(thd_percentage[idx_bass])
            max_thd_bass = np.max(thd_percentage[idx_bass])"""

new_bass = """        if len(idx_bass) > 0:
            avg_thd_bass = np.clip(np.mean(thd_percentage[idx_bass]), 0, 100)
            max_thd_bass = np.clip(np.max(thd_percentage[idx_bass]), 0, 100)"""
content = content.replace(old_bass, new_bass)

with open('analysis.py', 'w') as f:
    f.write(content)
