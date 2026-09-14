import sys

with open('main.py', 'r') as f:
    content = f.read()

old_theme_toggle = """    def on_theme_toggle(self):
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

new_theme_toggle = """    def on_theme_toggle(self):
        theme.toggle_theme(self)
        
        # Explicitly force plot widget backgrounds and axes just in case
        bg = theme.get_color('pg_bg')
        fg = theme.get_color('pg_fg')
        
        plots = [self.plot_widget]
        if hasattr(self, 'page_ana'):
            plots.extend([self.page_ana.plot_widget, self.page_ana.thd_widget, self.page_ana.csd_widget])
            
        for p in plots:
            p.setBackground(bg)
            p.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
            ax_l = p.getAxis('left')
            ax_b = p.getAxis('bottom')
            if ax_l:
                ax_l.setPen(fg)
                ax_l.setTextPen(fg)
            if ax_b:
                ax_b.setPen(fg)
                ax_b.setTextPen(fg)
                
            # Update title color if any
            if hasattr(p, 'titleLabel') and p.titleLabel.text:
                p.setTitle(p.titleLabel.text, color=fg, size="14pt")
            
        self.update_watermark()
        self.redraw_graph()"""

content = content.replace(old_theme_toggle, new_theme_toggle)

with open('main.py', 'w') as f:
    f.write(content)
