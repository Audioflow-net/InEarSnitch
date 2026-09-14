import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Add progress_callback to measure call
old_measure_call = """                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f,
                                                mic_cal_mags=self.cal_m)"""
new_measure_call = """                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f,
                                                mic_cal_mags=self.cal_m,
                                                progress_callback=lambda t, s=i+1: self.sweep_progress.emit(t, s))"""
code = code.replace(old_measure_call, new_measure_call)

# 2. Connect sweep_progress in run_measurement
old_connect = """        self.worker.progress.connect(update_overlay)
        self.worker.start()"""
new_connect = """        self.worker.progress.connect(update_overlay)
        self.worker.sweep_progress.connect(self.meas_overlay.update_anim_sync)
        self.worker.start()"""
code = code.replace(old_connect, new_connect)

with open("main.py", "w") as f:
    f.write(code)

print("MeasurementWorker fully patched.")
