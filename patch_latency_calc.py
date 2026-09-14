import re

with open('audio_engine.py', 'r') as f:
    content = f.read()

old_code = r"""        latency_samples = peak_index - \(len\(ir\) // 2\)"""

new_code = """        # FIX: Since rec_signal is now padded to 1.5s but inv_sweep is 1.0s, 
        # mode='same' places the zero-latency peak at len(inv_sweep) // 2, not len(ir) // 2.
        latency_samples = peak_index - (len(inv_sweep) // 2)"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    with open('audio_engine.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
