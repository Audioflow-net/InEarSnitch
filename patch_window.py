import re

with open('main.py', 'r') as f:
    content = f.read()

content = content.replace(
    'sig_w = sig * window',
    'sig_w = sig * window[:len(sig)] if len(sig) <= len(window) else sig * np.hanning(len(sig))'
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
