import re

with open("test_jig_v2.scad", "r") as f:
    content = f.read()

# Replace the thread subtraction with a fast preview fallback
new_thread_call = """
        if ($preview) {
            // Im F5 Preview nur einen simplen Zylinder abziehen, sonst laggt es!
            translate([0, 0, -1]) cylinder(d=coupler_thread_d, h=10);
        } else {
            // Beim F6 Rendern echtes Gewinde abziehen
            Bulletproof_Thread(d=coupler_thread_d, pitch=thread_pitch, turns=thread_turns);
        }
"""

content = content.replace("Bulletproof_Thread(d=coupler_thread_d, pitch=thread_pitch, turns=thread_turns);", new_thread_call)

with open("test_jig_v2.scad", "w") as f:
    f.write(content)
