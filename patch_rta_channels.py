import re
import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Update LiveSealWorker
old_worker_init = """    def __init__(self, in_idx, out_idx, cal_f=None, cal_m=None):
        super().__init__()
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.running = True
        self.fs = 48000
        self.blocksize = 8192"""

new_worker_init = """    def __init__(self, in_idx, out_idx, cal_f=None, cal_m=None, target_channel="Left"):
        super().__init__()
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.target_channel = target_channel
        self.running = True
        self.fs = 48000
        self.blocksize = 8192

    def set_target_channel(self, target_channel):
        self.target_channel = target_channel"""

content = content.replace(old_worker_init, new_worker_init)

old_worker_out = """                outdata[:, 0] = pn
                if outdata.shape[1] > 1:
                    outdata[:, 1] = pn"""

new_worker_out = """                if self.target_channel == "Left":
                    outdata[:, 0] = pn
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = 0.0
                else:
                    outdata[:, 0] = 0.0
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = pn"""

content = content.replace(old_worker_out, new_worker_out)

# 2. Add connection for live changing in main.py
if "self.btn_grp_chan.buttonClicked.connect(self.on_target_channel_changed)" not in content:
    content = content.replace("self.btn_grp_chan.buttonClicked.connect(self.update_watermark)", "self.btn_grp_chan.buttonClicked.connect(self.update_watermark)\n        self.btn_grp_chan.buttonClicked.connect(self.on_target_channel_changed)")

# 3. Add on_target_channel_changed method to IE_SNITCH class
if "def on_target_channel_changed(self):" not in content:
    method = """
    def on_target_channel_changed(self):
        import pyqtgraph as pg
        import theme
        if hasattr(self, 'live_worker') and self.live_worker.running:
            self.live_worker.set_target_channel(self.get_current_channel())
            color = theme.get_color('curve_left') if self.get_current_channel() == "Left" else theme.get_color('curve_right')
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                self.live_rta_line.setPen(pg.mkPen(color, width=2))
"""
    # Insert it right before def get_current_channel
    content = content.replace("    def get_current_channel(self):", method + "\n    def get_current_channel(self):")

# 4. Update toggle_live_seal to pass the target channel and use the right color
old_toggle = """            self.live_rta_line = target_plot.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")"""
new_toggle = """            color = theme.get_color('curve_left') if self.get_current_channel() == "Left" else theme.get_color('curve_right')
            self.live_rta_line = target_plot.plot(pen=pg.mkPen(color, width=2), name="Live Seal")"""
content = content.replace(old_toggle, new_toggle)

old_worker_start = """            self.live_worker = LiveSealWorker(self.selected_in_idx, self.selected_out_idx, cal_f, cal_m)"""
new_worker_start = """            self.live_worker = LiveSealWorker(self.selected_in_idx, self.selected_out_idx, cal_f, cal_m, target_channel=self.get_current_channel())"""
content = content.replace(old_worker_start, new_worker_start)

with open('main.py', 'w') as f:
    f.write(content)
