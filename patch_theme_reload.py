import re

with open('main.py', 'r') as f:
    content = f.read()

# Fix literal string styles to use classes
content = content.replace('lbl_in.setStyleSheet("color: {theme.get_color(\\"text_secondary\\")}; font-size: 12px;")', 'lbl_in.setProperty("class", "subtitle")\n        lbl_in.style().unpolish(lbl_in)\n        lbl_in.style().polish(lbl_in)')
content = content.replace('lbl_out.setStyleSheet("color: {theme.get_color(\\"text_secondary\\")}; font-size: 12px;")', 'lbl_out.setProperty("class", "subtitle")\n        lbl_out.style().unpolish(lbl_out)\n        lbl_out.style().polish(lbl_out)')
content = content.replace('lbl_mic.setStyleSheet(f"color: {theme.get_color(\'text_secondary\')}; font-size: 12px;")', 'lbl_mic.setProperty("class", "subtitle")\n        lbl_mic.style().unpolish(lbl_mic)\n        lbl_mic.style().polish(lbl_mic)')
content = content.replace('lbl_smooth.setStyleSheet("color: {theme.get_color(\\"text_secondary\\")}; font-weight: bold;")', 'lbl_smooth.setProperty("class", "subtitle")\n        lbl_smooth.style().unpolish(lbl_smooth)\n        lbl_smooth.style().polish(lbl_smooth)')

# Safely rename page_set where it was initially created and used within setup_ui
def replace_page_set(match):
    return match.group(0).replace('page_set', 'self.page_set')
    
# Only replace page_set within setup_ui function
import re
content = re.sub(
    r'    def setup_ui\(self\):.*?(?=\n    def |\n$)',
    replace_page_set,
    content,
    flags=re.DOTALL
)

# Update apply_dynamic_theme_styles to refresh these hardcoded f-strings
dynamic_method = """    def apply_dynamic_theme_styles(self):
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
                
            if hasattr(p, 'titleLabel') and p.titleLabel.text:
                p.setTitle(p.titleLabel.text, color=fg, size="14pt")
        
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'update_theme'):
            self.page_ana.update_theme()
            
        panel_bg = theme.get_color('bg_panel')
        border = theme.get_color('border')
        if hasattr(self, 'control_panel'):
            self.control_panel.setStyleSheet(f"#ControlPanel {{ background-color: {panel_bg}; border-top: 1px solid {border}; border-radius: 8px; }}")
            
        if hasattr(self, 'active_tour') and self.active_tour is not None:
            self.active_tour.update_theme()

        # --- FULL REFRESH OF F-STRING STYLES ---
        if hasattr(self, 'page_set'):
            self.page_set.setStyleSheet(f"#SettingsPanel {{ background-color: {theme.get_color('bg_panel')}; border-left: 1px solid {theme.get_color('border')}; }}")
        if hasattr(self, 'manual_browser'):
            self.manual_browser.setStyleSheet(f"background-color: {theme.get_color('bg_main')}; color: {theme.get_color('text_primary')}; border: 1px solid {theme.get_color('border')}; border-radius: 4px; padding: 10px;")
        if hasattr(self, 'console_output'):
            self.console_output.setStyleSheet(f"background-color: {theme.get_color('bg_main')}; color: {theme.get_color('text_primary')}; font-family: 'Courier New', Courier, monospace; font-size: 11px; padding: 5px; border: 1px solid {theme.get_color('border')}; border-radius: 4px;")
        
        # Refresh main tabs
        if hasattr(self, 'workspace_stacked'):
            self.switch_workspace_tab(self.workspace_stacked.currentIndex())
"""

content = re.sub(
    r'    def apply_dynamic_theme_styles\(self\):.*?(?=\n    def |\n$)',
    dynamic_method,
    content,
    flags=re.DOTALL
)

# Update on_theme_toggle to include processEvents properly
toggle_method = """    def on_theme_toggle(self):
        theme.toggle_theme(self)
        self.apply_dynamic_theme_styles()
        self.update_watermark()
        self.redraw_graph()
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        self.repaint()
        
        # Re-apply card inline styles for the new theme
        active_card = None
        for c in self.profile_cards:
            if c.property("selected") == "true":
                active_card = c
            # Update AvatarButtons for the new theme
            for b_id, b in getattr(c, 'avatar_btns', []):
                b.update_style(b.property("selected") == "true")
                
        if active_card:
            self.force_profile_selection(active_card)
"""

content = re.sub(
    r'    def on_theme_toggle\(self\):.*?(?=\n    def |\n$)',
    toggle_method,
    content,
    flags=re.DOTALL
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
