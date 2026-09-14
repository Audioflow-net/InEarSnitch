import re

with open('main.py', 'r') as f:
    content = f.read()

live_seal_code = """
class LiveSealWorker(QThread):
    update_signal = pyqtSignal(object, object)
    error = pyqtSignal(str)

    def __init__(self, in_idx, out_idx, cal_f=None, cal_m=None):
        super().__init__()
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.running = True
        self.fs = 48000
        self.blocksize = 8192

    def run(self):
        import sounddevice as sd
        import numpy as np
        from scipy import interpolate
        
        def generate_pink_noise(N):
            X_white = np.fft.rfft(np.random.randn(N))
            S = np.sqrt(np.arange(X_white.size) + 1.0)
            y = np.fft.irfft(X_white / S)
            return (y / np.max(np.abs(y))) * 0.15 # -16dBFS roughly

        def callback(indata, outdata, frames, time, status):
            if not self.running:
                raise sd.CallbackStop
            
            pn = generate_pink_noise(frames)
            outdata[:, 0] = pn
            if outdata.shape[1] > 1:
                outdata[:, 1] = pn
                
            sig = indata[:, 0].copy()
            window = np.hanning(len(sig))
            sig_w = sig * window
            
            mag = np.abs(np.fft.rfft(sig_w))
            # Smooth RTA a bit to make it readable
            kernel_size = 15
            kernel = np.ones(kernel_size) / kernel_size
            mag_smooth = np.convolve(mag, kernel, mode='same')
            
            mag_db = 20 * np.log10(mag_smooth + 1e-12)
            freqs = np.fft.rfftfreq(len(sig), 1/self.fs)
            
            if self.cal_f is not None and self.cal_m is not None:
                interp_func = interpolate.interp1d(self.cal_f, self.cal_m, bounds_error=False, fill_value=0.0)
                mag_db += interp_func(freqs)
                
            self.update_signal.emit(freqs, mag_db)

        try:
            with sd.Stream(device=(self.in_idx, self.out_idx),
                           samplerate=self.fs, blocksize=self.blocksize,
                           channels=(1, 2), callback=callback):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            self.error.emit(str(e))
            
    def stop(self):
        self.running = False

class MeasurementWorker(QThread):"""

content = content.replace("class MeasurementWorker(QThread):", live_seal_code)

with open('main.py', 'w') as f:
    f.write(content)
