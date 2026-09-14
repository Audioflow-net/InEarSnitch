with open('audio_engine.py', 'r') as f:
    content = f.read()

# Fix the specific multi-line string issue
old_str = '''raise RuntimeError(f"Electrical Loopback Detected! The frequency response is completely flat ({mag_range:.1f} dB variance). You are measuring the soundcard itself, not the microphone.

Turn off 'Direct Monitoring' / 'Loopback' on your audio interface, and check your input selection.")'''

new_str = '''raise RuntimeError(f"Electrical Loopback Detected! The frequency response is completely flat ({mag_range:.1f} dB variance). You are measuring the soundcard itself, not the microphone.\\n\\nTurn off 'Direct Monitoring' / 'Loopback' on your audio interface, and check your input selection.")'''

content = content.replace(old_str, new_str)

with open('audio_engine.py', 'w') as f:
    f.write(content)

