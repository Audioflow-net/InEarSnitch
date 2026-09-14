import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# 1. Modify update_dsp inside __init__ to also update the visual line
old_update_dsp = r"""            def update_dsp\(checked=False, idx=i\):
                from eq_math import dsp_engine
                filters = \[\]
                for b in self\.peq_bands:
                    filters\.append\(\{
                        'enabled': b\['on'\]\.isChecked\(\),
                        'freq': b\['f'\]\.value\(\),
                        'gain': b\['g'\]\.value\(\),
                        'q': b\['q'\]\.value\(\),
                        'type': b\['type'\]
                    \}\)
                dsp_engine\.set_filters\(filters\)
                dsp_engine\.set_master\(self\.cb_dsp_enable\.isChecked\(\)\)"""

new_update_dsp = """            def update_dsp(checked=False, idx=i):
                from eq_math import dsp_engine
                filters = []
                for b in self.peq_bands:
                    filters.append({
                        'enabled': b['on'].isChecked(),
                        'freq': b['f'].value(),
                        'gain': b['g'].value(),
                        'q': b['q'].value(),
                        'type': b['type']
                    })
                dsp_engine.set_filters(filters)
                dsp_engine.set_master(self.cb_dsp_enable.isChecked())
                
                # Update Virtual EQ Line
                if hasattr(self, 'current_freqs') and self.current_freqs is not None:
                    if hasattr(self, 'virtual_eq_line') and self.virtual_eq_line is not None:
                        eq_delta = dsp_engine.get_magnitude_response(self.current_freqs, 48000)
                        base_mag = self.current_mag_l if self.current_mag_l is not None else self.current_mag_r
                        if base_mag is not None:
                            # Also smooth it slightly so it matches the visual smoothing of the main curve
                            from audio_engine import AudioEngine
                            f_eq, m_eq, _ = AudioEngine.smooth_spectrum(self.current_freqs, base_mag + eq_delta, points=240)
                            self.virtual_eq_line.setData(f_eq, m_eq)
                            if self.cb_dsp_enable.isChecked():
                                self.virtual_eq_line.show()
                            else:
                                self.virtual_eq_line.hide()"""

content = re.sub(old_update_dsp, new_update_dsp, content)


# 2. Modify update_plots to save freqs/mags and create virtual_eq_line
old_update_plots = r"""        report = Analyzer\.run_full_diagnostics\(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f\)
        
        # --- Update Diagnostics Plot ---
        self\.plot_widget\.clear\(\)"""

new_update_plots = """        report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f)
        
        # Save for virtual EQ
        self.current_freqs = freqs
        self.current_mag_l = mag_l
        self.current_mag_r = mag_r
        
        # --- Update Diagnostics Plot ---
        self.plot_widget.clear()
        
        import pyqtgraph as pg
        from PyQt5.QtCore import Qt
        # Create virtual EQ line early so it draws behind or in front as desired
        self.virtual_eq_line = self.plot_widget.plot(pen=pg.mkPen('#00FFFF', width=3, style=Qt.DotLine), name='Simulated EQ')
        self.virtual_eq_line.hide()"""

content = re.sub(old_update_plots, new_update_plots, content)


# 3. Trigger update_dsp at the end of update_plots so it draws immediately if enabled
old_end_plots = r"""                self\.csd_widget\.plot\(
                    shift_freqs, 
                    shift_mag, 
                    pen=pg\.mkPen\(color, width=1\.5\),
                    fillLevel=-100,
                    brush=pg\.mkBrush\('#18181b'\)
                \)"""

new_end_plots = """                self.csd_widget.plot(
                    shift_freqs, 
                    shift_mag, 
                    pen=pg.mkPen(color, width=1.5),
                    fillLevel=-100,
                    brush=pg.mkBrush('#18181b')
                )
                
        # Trigger EQ update to draw the virtual curve
        if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
            # We call the first band's toggled slot manually to force an update
            self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())"""
            
content = re.sub(old_end_plots, new_end_plots, content)

with open('analysis_ui.py', 'w') as f:
    f.write(content)

