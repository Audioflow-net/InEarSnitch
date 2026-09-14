import re

with open("audio_engine.py", "r") as f:
    code = f.read()

old_code = """        # Ensure it finishes gracefully
        sd.wait()
        if np.max(np.abs(recording)) < 1e-4:
            raise RuntimeError("Received pure silence. Check macOS Microphone permissions in System Settings -> Privacy & Security, or verify the correct Input Device is selected in the Settings tab.")
                               
        # 3. Deconvolution via FFT convolution to get Impulse Response (IR)
        ir = fftconvolve(recording[:, 0], inv_sweep, mode='same')"""

new_code = """        # Ensure it finishes gracefully
        sd.wait()
        
        rec_signal = recording[:, 0]
        peak_amp = np.max(np.abs(rec_signal))
        if peak_amp < 0.002: # -54 dBFS
            raise RuntimeError(f"Received pure silence (Peak: {peak_amp:.5f}). Check macOS Microphone permissions, or verify the correct Input Device is selected.")
                               
        # 3. Deconvolution via FFT convolution to get Impulse Response (IR)
        ir = fftconvolve(rec_signal, inv_sweep, mode='same')
        
        # SNR / Crest Factor Check to prevent "ghost" curves from background noise
        rms_ir = np.sqrt(np.mean(ir**2))
        crest_factor = 20 * np.log10(np.max(np.abs(ir)) / (rms_ir + 1e-12))
        if crest_factor < 25.0:
            raise RuntimeError(f"Measurement failed: No valid sweep detected in the recording (SNR too low, Crest Factor: {crest_factor:.1f} dB).\\n\\n"
                               "The microphone only picked up background noise. Ensure the IEM is playing sound and is properly seated in the coupler.")"""

code = code.replace(old_code, new_code)

with open("audio_engine.py", "w") as f:
    f.write(code)

print("SNR checks patched.")
