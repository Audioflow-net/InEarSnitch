import re

with open("audio_engine.py", "r") as f:
    code = f.read()

old_playrec = """        # 2. CoreAudio full-duplex I/O
        recording = sd.playrec(sweep_stereo, 
                               samplerate=self.sample_rate, 
                               channels=1, 
                               device=(input_device_idx, output_device_idx),
                               blocking=False)"""

new_playrec = """        # Dynamically adopt the output device's native sample rate if it differs
        try:
            out_info = sd.query_devices(output_device_idx)
            native_sr = int(out_info['default_samplerate'])
            if native_sr != self.sample_rate:
                self.sample_rate = native_sr
                sweep, _ = self.generate_sweep(duration, f_start, f_end)
                inv_sweep = self.get_inverse_filter(sweep, duration, f_start, f_end)
                sweep_stereo = np.zeros((len(sweep), 2))
                if target_channel == 'L':
                    sweep_stereo[:, 0] = sweep
                else:
                    sweep_stereo[:, 1] = sweep
        except Exception:
            pass

        # 2. CoreAudio full-duplex I/O
        try:
            recording = sd.playrec(sweep_stereo, 
                                   samplerate=self.sample_rate, 
                                   channels=1, 
                                   device=(input_device_idx, output_device_idx),
                                   blocking=False)
        except sd.PortAudioError as e:
            # Fallback for some macOS interfaces that strictly require matching input channels
            if "9986" in str(e) or "Internal PortAudio error" in str(e):
                in_info = sd.query_devices(input_device_idx)
                in_chans = in_info['max_input_channels']
                recording = sd.playrec(sweep_stereo, 
                                       samplerate=self.sample_rate, 
                                       channels=in_chans, # Use exact max input channels
                                       device=(input_device_idx, output_device_idx),
                                       blocking=False)
            else:
                raise e"""

code = code.replace(old_playrec, new_playrec)

with open("audio_engine.py", "w") as f:
    f.write(code)

print("Audio engine fallback patched.")
