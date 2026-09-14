import re

# 1. Patch audio_engine.py
with open("audio_engine.py", "r") as f:
    ae_code = f.read()

ae_old = """    def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=20.0, f_end=20000.0, mic_cal_freqs=None, mic_cal_mags=None):"""
ae_new = """    def measure(self, input_device_idx, output_device_idx, target_channel='L', duration=1.0, f_start=20.0, f_end=20000.0, mic_cal_freqs=None, mic_cal_mags=None, progress_callback=None):"""
ae_code = ae_code.replace(ae_old, ae_new)

ae_loop_old = """        # Wait for the stream to finish or timeout
        while sd.get_stream() is not None and sd.get_stream().active:
            if time.time() - start_t > timeout:
                sd.stop()
                raise RuntimeError("Audio Engine Timeout: The audio interface did not respond. Check macOS Microphone permissions.")"""
ae_loop_new = """        # Wait for the stream to finish or timeout
        while sd.get_stream() is not None and sd.get_stream().active:
            if progress_callback:
                progress_callback(time.time() - start_t)
            time.sleep(0.015) # 60fps UI update rate
            if time.time() - start_t > timeout:
                sd.stop()
                raise RuntimeError("Audio Engine Timeout: The audio interface did not respond. Check macOS Microphone permissions.")"""
ae_code = ae_code.replace(ae_loop_old, ae_loop_new)

with open("audio_engine.py", "w") as f:
    f.write(ae_code)

# 2. Patch main.py
with open("main.py", "r") as f:
    main_code = f.read()

# Add signal to MeasurementWorker
mw_old = """class MeasurementWorker(QThread):
    finished = pyqtSignal(object, object, object, object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)"""
mw_new = """class MeasurementWorker(QThread):
    finished = pyqtSignal(object, object, object, object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    sweep_progress = pyqtSignal(float, int)"""
main_code = main_code.replace(mw_old, mw_new)

# Add callback in MeasurementWorker.run
mw_run_old = """            for i in range(self.sweeps):
                self.progress.emit(f"Status: MEASURING {self.target_channel}... ({i+1}/{self.sweeps})")
                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f, 
                                                mic_cal_mags=self.cal_m)"""
mw_run_new = """            for i in range(self.sweeps):
                self.progress.emit(f"Status: MEASURING {self.target_channel}... ({i+1}/{self.sweeps})")
                
                def on_prog(t, current_sweep=i+1):
                    self.sweep_progress.emit(t, current_sweep)
                    
                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f, 
                                                mic_cal_mags=self.cal_m,
                                                progress_callback=on_prog)"""
main_code = main_code.replace(mw_run_old, mw_run_new)

# Connect in main.py start_measurement
start_m_old = """        self.worker.progress.connect(self.update_status)
        
        self.btn_capture.setEnabled(False)"""
start_m_new = """        self.worker.progress.connect(self.update_status)
        self.worker.sweep_progress.connect(self.update_anim_sync)
        
        self.btn_capture.setEnabled(False)"""
main_code = main_code.replace(start_m_old, start_m_new)

# Fix setup_anim (remove QTimer)
anim_old = """        self.timer = QTimer()
        self.timer.timeout.connect(self.update_anim)
        self.sweeps = 1
        self.start_time = 0
        
    def start(self, sweeps):
        self.sweeps = sweeps
        self.start_time = time.time()
        self.set_text(f"SWEEP 1 / {sweeps}")
        self.lbl.show()
        self.sweep_line.show()
        self.region.show()
        self.timer.start(16)"""
anim_new = """        self.sweeps = 1
        
    def start(self, sweeps):
        self.sweeps = sweeps
        self.set_text(f"SWEEP 1 / {sweeps}")
        self.lbl.show()
        self.sweep_line.show()
        self.region.show()"""
main_code = main_code.replace(anim_old, anim_new)

# Replace update_anim with update_anim_sync
anim_update_old = """    def update_anim(self):
        import time
        import math
        
        # Center the HUD text dynamically
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        self.lbl.setPos(rect.width()/2, rect.height()/2)
        
        t = time.time() - self.start_time
        
        cycle_t = t % 1.2
        if cycle_t <= 1.0:
            freq = 20 * (1000 ** cycle_t)
            x_pos = math.log10(freq)
            self.sweep_line.setValue(x_pos)
            self.region.setRegion([math.log10(20), x_pos])
            self.sweep_line.show()
            self.region.show()
        else:
            self.sweep_line.hide()
            self.region.hide()
            
        if self.sweeps > 1:
            sweep_num = min(int(t / 1.2) + 1, self.sweeps)
            self.set_text(f"SWEEP {sweep_num} / {self.sweeps}")"""
anim_update_new = """    def update_anim_sync(self, t_elapsed, sweep_num):
        import math
        
        # Center the HUD text dynamically
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        self.lbl.setPos(rect.width()/2, rect.height()/2)
        
        if self.sweeps > 1:
            self.set_text(f"SWEEP {sweep_num} / {self.sweeps}")
            
        if t_elapsed <= 1.0:
            freq = 20 * (1000 ** t_elapsed)
            # Clamp freq just in case
            freq = max(20, min(20000, freq))
            x_pos = math.log10(freq)
            self.sweep_line.setValue(x_pos)
            self.region.setRegion([math.log10(20), x_pos])
            self.sweep_line.show()
            self.region.show()
        else:
            self.sweep_line.hide()
            self.region.hide()"""
main_code = main_code.replace(anim_update_old, anim_update_new)

# Replace stop timer
stop_old = """    def stop(self):
        self.timer.stop()
        self.sweep_line.hide()"""
stop_new = """    def stop(self):
        self.sweep_line.hide()"""
main_code = main_code.replace(stop_old, stop_new)

with open("main.py", "w") as f:
    f.write(main_code)

print("Animation sync patched.")
