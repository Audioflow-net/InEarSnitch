with open('audio_engine.py', 'r') as f:
    content = f.read()

import re

old_logic = r"""        # PRO-AUDIO UPDATE: Onset detection \(5% threshold of peak\)
        # We align to the onset to preserve real physical group delay \(Time of Flight\)\.
        peak_amp_ir = np\.max\(np\.abs\(ir\)\)
        threshold = 0\.05 \* peak_amp_ir
        onset_indices = np\.where\(np\.abs\(ir\) > threshold\)\[0\]
        onset_idx = onset_indices\[0\] if len\(onset_indices\) > 0 else np\.argmax\(np\.abs\(ir\)\)
        
        # Window: -5ms before onset to \+300ms after onset \(perfectly captures sub-bass without cutting group delay\)
        win_pre = int\(0\.005 \* self\.sample_rate\)
        win_post = int\(0\.3 \* self\.sample_rate\)
        w_start = max\(0, onset_idx - win_pre\)
        w_end = min\(N, onset_idx \+ win_post\)"""

new_logic = """        # FIX: The global 'np.where' onset detection was catching Farina's harmonic distortion 
        # impulses (-81ms before the peak) if distortion was > 5%, causing catastrophic 
        # comb-filtering by windowing both the distortion and the main impulse!
        
        peak_idx = np.argmax(np.abs(ir))
        peak_amp_ir = np.abs(ir[peak_idx])
        
        # PRO-AUDIO UPDATE: Localized Onset detection
        # We only search up to 2ms *before* the main peak. This guarantees we find the true 
        # acoustic onset of the main impulse, completely ignoring Farina distortion impulses!
        search_pre = int(0.002 * self.sample_rate)
        search_start = max(0, peak_idx - search_pre)
        
        threshold = 0.05 * peak_amp_ir
        local_search_area = np.abs(ir[search_start:peak_idx])
        above_thresh = np.where(local_search_area > threshold)[0]
        
        if len(above_thresh) > 0:
            onset_idx = search_start + above_thresh[0]
        else:
            onset_idx = peak_idx
            
        # Window: -5ms before onset to +100ms after onset
        # (100ms perfectly captures sub-bass down to 10Hz in IEMs without grabbing too much noise)
        win_pre = int(0.005 * self.sample_rate)
        win_post = int(0.10 * self.sample_rate)
        w_start = max(0, onset_idx - win_pre)
        w_end = min(N, onset_idx + win_post)"""

if re.search(old_logic, content):
    content = re.sub(old_logic, new_logic, content)
    with open('audio_engine.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
