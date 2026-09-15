import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# We need to replace the `for item in self._last_report:` loop.
loop_start = "        for item in self._last_report:"
loop_end = "        self.report_layout.addStretch()"

old_loop_code = content[content.find(loop_start) : content.find(loop_end)]

new_loop_code = """        left_items = []
        right_items = []
        gen_items = []
        
        for item in self._last_report:
            cat = item.get('category', 'FR')
            if active_cat is not None and cat != active_cat:
                continue
                
            title = item.get('title', '')
            if title.startswith('Left '):
                left_items.append(item)
            elif title.startswith('Right '):
                right_items.append(item)
            else:
                gen_items.append(item)
                
        def create_header(text, color="#06b6d4"):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {color}; font-weight: 900; font-size: 10px; letter-spacing: 2px; padding-top: 8px; padding-bottom: 2px;")
            return lbl

        def render_group(items, header_text, header_color):
            if not items: return
            self.report_layout.addWidget(create_header(header_text, header_color))
            for item in items:
                status = item.get('status', 'OK')
                bg, accent, icon = status_style.get(status, status_style['OK'])
                band = item.get('band')
                cat = item.get('category', 'FR')

                card = QFrame()
                card.setCursor(Qt.PointingHandCursor if band else Qt.ArrowCursor)
                card.setStyleSheet(f"QFrame {{ background: {bg}; border-left: 3px solid {accent}; border-radius: 3px; padding: 3px 6px; margin: 1px 0; }}")
                cl = QVL(card)
                cl.setContentsMargins(4, 2, 4, 2)
                cl.setSpacing(0)

                hdr = QLabel(f"<span style='color:{accent};font-weight:bold;'>{icon}</span>  <b>{item.get('title','')}</b>  <span style='color:{'#52525b' if is_light else '#666'};font-size:9px;'>[{cat}]</span>")
                hdr.setStyleSheet(f"color: {accent}; font-size: 11px; background: transparent; border: none;")
                cl.addWidget(hdr)

                desc = AutoWrapLabel(item.get('desc', ''))
                desc.setStyleSheet(f"color: {'#3f3f47' if is_light else '#999'}; font-size: 10px; background: transparent; border: none; padding-left: 16px;")
                cl.addWidget(desc)

                if band:
                    def make_zoom(b=band, c=cat):
                        def zoom_handler(event):
                            f_min, f_max = b
                            if c == 'THD':
                                self.graph_tabs.setCurrentIndex(1)
                                self.thd_widget.setXRange(np.log10(f_min), np.log10(f_max), padding=0.1)
                            elif c == 'CSD':
                                self.graph_tabs.setCurrentIndex(2)
                                self.csd_widget.setXRange(np.log10(f_min), np.log10(f_max), padding=0.1)
                            else:
                                self.graph_tabs.setCurrentIndex(0)
                                self.plot_widget.setXRange(np.log10(f_min), np.log10(f_max), padding=0.1)
                        return zoom_handler
                    card.mousePressEvent = make_zoom(band, cat)

                self.report_layout.addWidget(card)
                
        render_group(left_items, "LEFT EAR", "#3b82f6")
        render_group(right_items, "RIGHT EAR", "#ef4444")
        render_group(gen_items, "STEREO / GENERAL", "#10b981")
"""

content = content.replace(old_loop_code, new_loop_code)

with open("analysis_ui.py", "w") as f:
    f.write(content)
