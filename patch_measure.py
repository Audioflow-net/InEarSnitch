import re

with open("audio_engine.py", "r") as f:
    code = f.read()

old_measure = """    def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=20.0, f_end=20000.0, mic_cal_freqs=None, mic_cal_mags=None, progress_callback=None):"""
new_measure = """    def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=5.0, f_end=24000.0, mic_cal_freqs=None, mic_cal_mags=None, progress_callback=None):"""

code = code.replace(old_measure, new_measure)

with open("audio_engine.py", "w") as f:
    f.write(code)

print("measure patched.")
