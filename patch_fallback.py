import re

with open('audio_engine.py', 'r') as f:
    content = f.read()

old_code = r"""            if "9986" in str\(e\) or "Internal PortAudio error" in str\(e\):"""

new_code = """            if "9986" in str(e) or "9998" in str(e) or "Invalid number of channels" in str(e) or "Internal PortAudio error" in str(e):"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    with open('audio_engine.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
