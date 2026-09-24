with open("analysis_ui.py", "r") as f:
    content = f.read()

new_content = """        if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
            self.tip_analysis_card.update_theme()
            
        # Redraw diagnostics cards to refresh their light/dark color palette"""

content = content.replace("# Redraw diagnostics cards to refresh their light/dark color palette", new_content)

with open("analysis_ui.py", "w") as f:
    f.write(content)
