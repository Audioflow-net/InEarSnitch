import re

with open('main.py', 'r') as f:
    content = f.read()

# Patch LiveSealWorker
worker_old = "                pn = generate_pink_noise(frames)"
worker_new = """                pn = generate_pink_noise(frames)
                
                # Apply Hardware DSP if enabled
                from eq_math import dsp_engine
                if dsp_engine.master_enabled:
                    pn = dsp_engine.process(pn, self.fs)"""
                    
content = content.replace(worker_old, worker_new)

with open('main.py', 'w') as f:
    f.write(content)


with open('audio_engine.py', 'r') as f:
    ae_content = f.read()
    
ae_old = "        return sweep"
ae_new = """        # Apply Hardware DSP if enabled
        from eq_math import dsp_engine
        if dsp_engine.master_enabled:
            sweep = dsp_engine.process(sweep, fs)
            
        return sweep"""
        
ae_content = ae_content.replace(ae_old, ae_new)

with open('audio_engine.py', 'w') as f:
    f.write(ae_content)

