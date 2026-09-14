import re

with open('audio_engine.py', 'r') as f:
    content = f.read()

old_code = r"""        # Create stereo output array, but only populate the target channel
        sweep_stereo = np\.zeros\(\(len\(sweep\), 2\)\)
        if target_channel == 'L':
            sweep_stereo\[:, 0\] = sweep
        else:
            sweep_stereo\[:, 1\] = sweep"""

new_code = """        # FIX HF CUTOFF: Add 0.5s of silence at the end of the playback array!
        # If we don't zero-pad, sd.playrec stops recording the exact millisecond the 1s sweep 
        # is done outputting. But because of USB round-trip latency, the highest frequencies 
        # (which sit at the very end of the sweep) haven't reached the microphone yet! 
        # This truncates the HF and causes the graph to drop off a cliff above 10kHz.
        padding_samples = int(0.5 * self.sample_rate)
        sweep_stereo = np.zeros((len(sweep) + padding_samples, 2))
        if target_channel == 'L':
            sweep_stereo[:len(sweep), 0] = sweep
        else:
            sweep_stereo[:len(sweep), 1] = sweep"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    
    # Also need to fix the dynamically adopted sample rate block
    old_code2 = r"""                sweep_stereo = np\.zeros\(\(len\(sweep\), 2\)\)
                if target_channel == 'L':
                    sweep_stereo\[:, 0\] = sweep
                else:
                    sweep_stereo\[:, 1\] = sweep"""
                    
    new_code2 = """                padding_samples = int(0.5 * self.sample_rate)
                sweep_stereo = np.zeros((len(sweep) + padding_samples, 2))
                if target_channel == 'L':
                    sweep_stereo[:len(sweep), 0] = sweep
                else:
                    sweep_stereo[:len(sweep), 1] = sweep"""
                    
    content = re.sub(old_code2, new_code2, content)
    
    with open('audio_engine.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
