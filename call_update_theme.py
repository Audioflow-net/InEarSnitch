with open("main.py", "r") as f:
    content = f.read()

new_content = """        if hasattr(self, 'page_hist') and hasattr(self.page_hist, 'update_theme'):
            self.page_hist.update_theme()
            
        # Refresh main tabs"""

content = content.replace("# Refresh main tabs", new_content)

with open("main.py", "w") as f:
    f.write(content)
