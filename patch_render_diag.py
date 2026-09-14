import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

dynamic_method = """    def update_theme(self):
        import theme
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        active = theme.get_color('bg_hover')
        text_sec = theme.get_color('text_secondary')
        
        # Update Tabs
        self.graph_tabs.setStyleSheet(f"QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 6px 14px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        if hasattr(self, 'tools_tabs'):
            self.tools_tabs.setStyleSheet(f"QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 6px 14px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
            
        # Update Graph Backgrounds
        pg_bg = theme.get_color('pg_bg')
        if hasattr(self, 'plot_widget'):
            self.plot_widget.setBackground(pg_bg)
        if hasattr(self, 'thd_widget'):
            self.thd_widget.setBackground(pg_bg)
        if hasattr(self, 'csd_widget'):
            self.csd_widget.setBackground(pg_bg)
            
        # Update EQ mini plots and labels
        if hasattr(self, 'preset_cards_layout'):
            for i in range(self.preset_cards_layout.count()):
                item = self.preset_cards_layout.itemAt(i)
                if item and item.widget():
                    card = item.widget()
                    # Reapply styling to the card to trigger the patched setter
                    if hasattr(card, '_original_qss'):
                        card.setStyleSheet(card._original_qss)
                    from PySide6.QtWidgets import QLabel
                    for child in card.findChildren(QLabel):
                        if hasattr(child, '_original_qss'):
                            child.setStyleSheet(child._original_qss)
                    # The mini plots need explicit updating
                    import pyqtgraph as pg
                    for child in card.findChildren(pg.PlotWidget):
                        child.setBackground(theme.get_color('bg_main'))
                        
        # Redraw diagnostics cards to refresh their light/dark color palette
        self.render_diagnostics()
"""

content = re.sub(
    r'    def update_theme\(self\):.*?(?=\n    def |\n$)',
    dynamic_method,
    content,
    flags=re.DOTALL
)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
