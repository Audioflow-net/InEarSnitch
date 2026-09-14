with open('main.py', 'r') as f:
    content = f.read()

content = content.replace(
    'self.console_output.setStyleSheet(" font-family: \'Courier New\', Courier, monospace; font-size: 11px; padding: 5px;")',
    'self.console_output.setStyleSheet(f"background-color: {theme.get_color(\'bg_main\')}; color: {theme.get_color(\'text_primary\')}; font-family: \'Courier New\', Courier, monospace; font-size: 11px; padding: 5px; border: 1px solid {theme.get_color(\'border\')}; border-radius: 4px;")'
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
