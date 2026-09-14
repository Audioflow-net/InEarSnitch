import sys

with open('analysis.py', 'r') as f:
    content = f.read()
    
old_block = """        return report

    @staticmethod"""

new_block = """        # 5. Automated THD Diagnostics
        if thd_data is not None:
            thd_freqs, thd_l, thd_r = thd_data
            if thd_l is not None:
                max_thd_l = np.max(thd_l)
                if max_thd_l > 3.0:
                    report.append({'title': 'Left THD Alert', 'status': 'FAIL', 'desc': f'Distortion reaches {max_thd_l:.1f}%! This is highly unusual for BA drivers. Check for mechanical buzzing or clipping.', 'band': None})
                elif max_thd_l > 1.0:
                    report.append({'title': 'Left THD Check', 'status': 'WARN', 'desc': f'Peak distortion is {max_thd_l:.1f}%. Acceptable for dynamic drivers at high volume, but slightly high for balanced armatures.', 'band': None})
                else:
                    report.append({'title': 'Left THD Check', 'status': 'OK', 'desc': f'Clean. Peak distortion is low ({max_thd_l:.1f}%).', 'band': None})
                    
            if thd_r is not None:
                max_thd_r = np.max(thd_r)
                if max_thd_r > 3.0:
                    report.append({'title': 'Right THD Alert', 'status': 'FAIL', 'desc': f'Distortion reaches {max_thd_r:.1f}%! Check for mechanical buzzing or clipping.', 'band': None})
                elif max_thd_r > 1.0:
                    report.append({'title': 'Right THD Check', 'status': 'WARN', 'desc': f'Peak distortion is {max_thd_r:.1f}%. Slightly high.', 'band': None})
                else:
                    report.append({'title': 'Right THD Check', 'status': 'OK', 'desc': f'Clean. Peak distortion is low ({max_thd_r:.1f}%).', 'band': None})

        return report

    @staticmethod"""

content = content.replace(old_block, new_block, 1) # Only replace the first occurrence!

with open('analysis.py', 'w') as f:
    f.write(content)
