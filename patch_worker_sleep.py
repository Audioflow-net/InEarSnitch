import re

with open("main.py", "r") as f:
    code = f.read()

old_sleep = "time.sleep(0.2) # small pause between sweeps"
new_sleep = "time.sleep(1.0) # safely let PortAudio tear down the previous stream"

code = code.replace(old_sleep, new_sleep)

with open("main.py", "w") as f:
    f.write(code)

print("MeasurementWorker sleep patched.")
