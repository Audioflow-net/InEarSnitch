import re

with open('manual_en.md', 'r', encoding='utf-8') as f:
    content = f.read()

old_section = r'## 4\. Analysis and Automated Diagnostics Engine.*?## 5\. History Vault'
new_section = """## 4. Automated Diagnostics Engine

The "Automated Diagnostics Engine" (in the Analysis tab) evaluates your measurement to detect hardware defects or user errors automatically. The acoustic thresholds are based on industry standards and psychoacoustic literature (e.g., IEC 711 standards).

### How the diagnostics work (and why they are strict):

*   **Relative Phase (Polarity Inversion):**
    The engine does *not* check if a single IEM has an "absolute" phase inversion. Absolute phase is often introduced by soundcards, cables, or intentional crossover designs (like in multi-BA IEMs), and is generally inaudible to the human ear.
    Instead, the engine checks for **relative phase**: Are the left and right channels wired *oppositely*? If they are out of phase with each other, a strict FAIL is triggered. A relative phase mismatch leads to massive bass cancellation and the collapse of the stereo image. (In this case, check if your 2-pin/MMCX cables are inserted correctly).

*   **Bass / Acoustic Seal Leak:**
    The engine compares the bass region (50 Hz) against the midrange (1 kHz).
    - **WARNING:** Triggered when the bass drops by at least -10 dB compared to 1 kHz. For a neutral in-ear monitor (e.g., Etymotic or Diffuse-Field tuning), a drop of -2 to -6 dB is completely normal. A drop of -10 dB or more strongly indicates that the IEM is not optimally sealed in the measurement tube (leakage).
    - **FAIL:** Triggered only at -18 dB or worse. Such an extreme, steep drop in the low frequencies behaves physically like a high-pass filter, proving a massive air leak (seal break) in the coupler or a completely dead dynamic driver.

*   **Highs / Wax Clog:**
    A common flaw in simple measurement systems is checking exactly *one* specific frequency (e.g., 5 kHz). However, measurement tubes (IEC 711) have natural standing waves, often creating extremely narrow, deep dips (notches) precisely in this range.
    To avoid false alarms, our engine calculates the **average energy across the entire 4 kHz to 8 kHz band**. A true acoustic filter clogged with earwax physically acts like a low-pass filter, attenuating this entire frequency band broadly. The software will only trigger an alarm if this broadband average drops extremely low (-15 dB for a WARNING, -20 dB for a FAIL).

## 5. History Vault"""

content = re.sub(old_section, new_section, content, flags=re.DOTALL)

with open('manual_en.md', 'w', encoding='utf-8') as f:
    f.write(content)
