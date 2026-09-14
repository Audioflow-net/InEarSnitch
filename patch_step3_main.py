import sys
import re

with open('main.py', 'r') as f:
    content = f.read()

# Fix update_analysis_view logic in main.py
old_logic = """        if live_f is not None:
            primary_f = live_f
            primary_ml = live_ml
            primary_mr = live_mr
            primary_source = "live"
        elif hist_f is not None:
            primary_f = hist_f
            primary_ml = hist_ml
            primary_mr = hist_mr
            primary_source = "history"
            thd_data = None
            csd_data = None
            ir_l = None
            ir_r = None
        elif tgt_f is not None:
            primary_f = tgt_f
            primary_ml = tgt_m
            primary_mr = None
            primary_source = "target"
            thd_data = None
            csd_data = None
            ir_l = None
            ir_r = None

        if primary_f is None:
            self.page_ana.update_analysis(None, None, None)
            return

        # 3. Determine REFERENCE curves
        ref_mag_l = None
        ref_mag_r = None
        
        if primary_source == "live" and hist_f is not None:
            import numpy as np
            if hist_ml is not None:
                ref_mag_l = np.interp(primary_f, hist_f, hist_ml)
            if hist_mr is not None:
                ref_mag_r = np.interp(primary_f, hist_f, hist_mr)
                
        out_tgt_f = tgt_f if primary_source != "target" else None
        out_tgt_m = tgt_m if primary_source != "target" else None"""

new_logic = """        import numpy as np
        # Pass EVERYTHING independently so Analysis UI can render it.
        # If no live freqs, fallback to history freqs or target freqs as the x-axis base
        base_f = live_f if live_f is not None else (hist_f if hist_f is not None else tgt_f)
        
        if base_f is None:
            self.page_ana.update_analysis(None, None, None)
            return
            
        ref_mag_l = None
        ref_mag_r = None
        if hist_f is not None:
            if hist_ml is not None: ref_mag_l = np.interp(base_f, hist_f, hist_ml)
            if hist_mr is not None: ref_mag_r = np.interp(base_f, hist_f, hist_mr)
            
        out_tgt_f = tgt_f
        out_tgt_m = tgt_m"""

content = content.replace(old_logic, new_logic)

with open('main.py', 'w') as f:
    f.write(content)
