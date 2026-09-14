import sys

with open('main.py', 'r') as f:
    content = f.read()

old_theme_toggle = """    def on_theme_toggle(self):
        theme.toggle_theme(self)
        self.update_watermark()
        self.redraw_graph()"""

new_theme_toggle = """    def on_theme_toggle(self):
        theme.toggle_theme(self)
        
        # Explicitly force plot widget backgrounds just in case
        bg = theme.get_color('pg_bg')
        self.plot_widget.setBackground(bg)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        if hasattr(self, 'page_ana'):
            self.page_ana.plot_widget.setBackground(bg)
            self.page_ana.thd_widget.setBackground(bg)
            self.page_ana.csd_widget.setBackground(bg)
            self.page_ana.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
            self.page_ana.thd_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
            self.page_ana.csd_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
            
        self.update_watermark()
        self.redraw_graph()"""

content = content.replace(old_theme_toggle, new_theme_toggle)

with open('main.py', 'w') as f:
    f.write(content)
