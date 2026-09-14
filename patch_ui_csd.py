import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_ui = """        if csd_data is not None:
            # Expected format: (csd_freqs, csd_slices) where csd_slices is a list of arrays (mag values)
            csd_freqs, csd_slices = csd_data
            num_slices = len(csd_slices)
            
            # Draw from back to front (i.e. oldest/last slice first) to allow occlusion
            for i in range(num_slices - 1, -1, -1):
                slice_mag = csd_slices[i]
                
                # Isometric offset: shift slightly left in log space and down in magnitude
                shift_freqs = csd_freqs * (0.96 ** i)
                shift_mag = slice_mag - (i * 2.5)"""

new_ui = """        if csd_data is not None:
            show_l = self.btn_chan_l.isChecked()
            active_csd = csd_data.get('L') if show_l else csd_data.get('R')
            if active_csd:
                csd_freqs, csd_times, csd_slices = active_csd
                num_slices = len(csd_slices)
                
                # Draw from back to front (i.e. oldest/last slice first) to allow occlusion
                for i in range(num_slices - 1, -1, -1):
                    slice_mag = csd_slices[i]
                    
                    # Isometric offset: shift slightly left in log space and down in magnitude
                    shift_freqs = csd_freqs * (0.96 ** i)
                    shift_mag = slice_mag - (i * 2.5)"""
content = content.replace(old_ui, new_ui)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
