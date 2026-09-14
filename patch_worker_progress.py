import re

with open("main.py", "r") as f:
    code = f.read()

# At the end of the measure loop, emit a >1 value to force hiding the bar during sleep
pattern = r'''                irs\.append\(res\[3\]\)
                if self\.sweeps > 1 and i < self\.sweeps - 1:
                    time\.sleep\(1\.0\) # safely let PortAudio tear down the previous stream'''

replacement = r'''                irs.append(res[3])
                if self.sweeps > 1 and i < self.sweeps - 1:
                    self.sweep_progress.emit(1.1, i+1) # Hide bar during sleep
                    time.sleep(1.0) # safely let PortAudio tear down the previous stream'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Worker progress patched.")
