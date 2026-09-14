import re

with open('main.py', 'r') as f:
    content = f.read()

new_method = """    def style_tab(self, btn, active):
        if active:
            btn.setStyleSheet(f"color: {theme.get_color('text_primary')}; font-weight: bold; background-color: {theme.get_color('bg_panel')}; border-radius: 4px; padding: 10px 20px; border: 1px solid transparent; border-bottom: 2px solid {theme.get_color('accent')};")
        else:
            btn.setStyleSheet(f"color: {theme.get_color('text_secondary')}; font-weight: bold; background-color: {theme.get_color('bg_main')}; border-radius: 4px; padding: 10px 20px; border: 1px solid transparent; border-bottom: 2px solid transparent;")
"""

# Replace the existing style_tab method
content = re.sub(
    r'    def style_tab\(self, btn, active\):.*?(?=\n    def |\n$)',
    new_method,
    content,
    flags=re.DOTALL
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
