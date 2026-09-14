import re

with open('main.py', 'r') as f:
    content = f.read()

# Make update_live_rta print
new_update = """    def update_live_rta(self, freqs, mag_db):
        import numpy as np
        if not hasattr(self, '_rta_debug_count'): self._rta_debug_count = 0
        self._rta_debug_count += 1
        if self._rta_debug_count % 10 == 0: print(f"[LiveRTA] freqs: {len(freqs)}, mag: {np.mean(mag_db):.1f}dB")
        mask = (freqs >= 20) & (freqs <= 20000)
        
        # Smooth shift calculation over a broader range (e.g. 500Hz to 2000Hz)
        mask_1k = (freqs >= 500) & (freqs <= 2000)
        current_mean = np.mean(mag_db[mask_1k])
        
        # Exponential moving average for the shift so it doesn't jump wildly
        target_db = 85.0
        calculated_shift = target_db - current_mean
        
        if not hasattr(self, '_rta_shift'):
            self._rta_shift = calculated_shift
        else:
            self._rta_shift = 0.8 * self._rta_shift + 0.2 * calculated_shift
            
        self.live_rta_line.setData(freqs[mask], mag_db[mask] + self._rta_shift)"""

content = re.sub(r"    def update_live_rta\(self, freqs, mag_db\):.*?self\.live_rta_line\.setData\(freqs\[mask\], mag_db\[mask\] \+ self\._rta_shift\)", new_update, content, flags=re.DOTALL)

# Make LiveSealWorker callback print exceptions
new_callback = """        def callback(indata, outdata, frames, time, status):
            if not self.running:
                raise sd.CallbackStop
            try:
                pn = generate_pink_noise(frames)
                outdata[:, 0] = pn
                if outdata.shape[1] > 1:
                    outdata[:, 1] = pn
                    
                sig = indata[:, 0].copy()
                window = np.hanning(len(sig))
                sig_w = sig * window
                
                mag = np.abs(np.fft.rfft(sig_w))
                kernel_size = 15
                kernel = np.ones(kernel_size) / kernel_size
                mag_smooth = np.convolve(mag, kernel, mode='same')
                
                mag_db = 20 * np.log10(mag_smooth + 1e-12)
                freqs = np.fft.rfftfreq(len(sig), 1/self.fs)
                
                if self.cal_f is not None and self.cal_m is not None:
                    interp_func = interpolate.interp1d(self.cal_f, self.cal_m, bounds_error=False, fill_value=0.0)
                    mag_db += interp_func(freqs)
                    
                self.update_signal.emit(freqs, mag_db)
            except Exception as e:
                print(f"[LiveSealWorker Error] {e}")
                self.error.emit(str(e))
                raise sd.CallbackAbort"""

content = re.sub(r"        def callback\(indata, outdata, frames, time, status\):.*?self\.update_signal\.emit\(freqs, mag_db\)", new_callback, content, flags=re.DOTALL)

# Also fix the plot initialization
new_toggle = """                import pyqtgraph as pg
                self.live_rta_line = self.plot_widget.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")"""

content = re.sub(r"                import pyqtgraph as pg\n                self\.live_rta_line = pg\.PlotCurveItem\(pen=pg\.mkPen\('#db2777', width=2\)\)\n                self\.plot_widget\.addItem\(self\.live_rta_line\)", new_toggle, content)

with open('main.py', 'w') as f:
    f.write(content)
