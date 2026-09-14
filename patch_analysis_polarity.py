import re

with open("analysis.py", "r") as f:
    code = f.read()

# Replace method signature
code = code.replace(
    "def absolute_checks(freqs, mag, channel):",
    "def absolute_checks(freqs, mag, ir, channel):"
)

# Inject the check before return report
insert_point = r'(        return report)'
new_code = r"""        if ir is not None and len(ir) > 0:
            peak_idx = np.argmax(np.abs(ir))
            if ir[peak_idx] < 0:
                report.append({'title': f'{channel} Polarity', 'status': 'FAIL', 'desc': 'Inverted Polarity detected! The driver is wired in reverse.', 'band': None})
            else:
                report.append({'title': f'{channel} Polarity', 'status': 'OK', 'desc': 'Acoustic polarity is correct (positive).', 'band': None})
                
\1"""

code = re.sub(insert_point, new_code, code, count=1)

with open("analysis.py", "w") as f:
    f.write(code)

print("Analysis polarity patched.")
