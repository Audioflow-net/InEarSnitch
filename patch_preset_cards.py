import sys
import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_load = """        # Clear existing cards
        for i in reversed(range(self.preset_cards_layout.count())): 
            w = self.preset_cards_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        try:
            conn = sqlite3.connect("inearsnitch.db")
            c = conn.cursor()
            c.execute("SELECT name FROM eq_presets ORDER BY name")
            rows = c.fetchall()
            conn.close()
            
            for row in rows:
                name = row[0]
                card = QFrame()
                card.setStyleSheet("QFrame { background: #222; border: 1px solid #333; border-radius: 6px; }")
                cl = QHBoxLayout(card)
                cl.setContentsMargins(8, 6, 8, 6)
                
                lbl = QLabel(name)
                lbl.setStyleSheet("font-weight: bold; font-size: 11px; color: #eee; border: none;")"""

new_load = """        # Clear existing cards
        for i in reversed(range(self.preset_cards_layout.count())): 
            w = self.preset_cards_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        try:
            import json, numpy as np
            import pyqtgraph as pg
            from audio_engine import AudioEngine
            conn = sqlite3.connect("inearsnitch.db")
            c = conn.cursor()
            c.execute("SELECT name, data FROM eq_presets ORDER BY name")
            rows = c.fetchall()
            conn.close()
            
            for row in rows:
                name, data_str = row
                bands = json.loads(data_str) if data_str else []
                
                card = QFrame()
                card.setStyleSheet("QFrame { background: #222; border: 1px solid #333; border-radius: 6px; }")
                cl = QHBoxLayout(card)
                cl.setContentsMargins(8, 6, 8, 6)
                
                lbl = QLabel(name)
                lbl.setStyleSheet("font-weight: bold; font-size: 11px; color: #eee; border: none;")
                
                # Mini Graph
                mini_plot = pg.PlotWidget()
                mini_plot.setFixedSize(50, 20)
                mini_plot.hideAxis('bottom')
                mini_plot.hideAxis('left')
                mini_plot.setBackground('#222')
                mini_plot.setMouseEnabled(x=False, y=False)
                mini_plot.setMenuEnabled(False)
                mini_plot.setLogMode(x=True, y=False)
                mini_plot.setXRange(np.log10(20), np.log10(20000))
                mini_plot.setYRange(-12, 12)
                
                f_mini = np.logspace(np.log10(20), np.log10(20000), 60)
                delta = np.zeros(60)
                for b in bands:
                    if b.get('on', True):
                        H = AudioEngine.calculate_biquad_response(b.get('type', 'peq'), b['f'], b['g'], b.get('q', 1.41), f_mini, 48000)
                        delta += 20 * np.log10(np.abs(H) + 1e-12)
                mini_plot.plot(f_mini, delta, pen=pg.mkPen('#0ea5e9', width=1.5))"""

content = content.replace(old_load, new_load)

# Also need to add mini_plot to layout
old_add = """                cl.addWidget(lbl, stretch=1)
                cl.addWidget(btn_load)
                cl.addWidget(btn_del)"""

new_add = """                cl.addWidget(lbl, stretch=1)
                cl.addWidget(mini_plot)
                cl.addWidget(btn_load)
                cl.addWidget(btn_del)"""

content = content.replace(old_add, new_add)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
