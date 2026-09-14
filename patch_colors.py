import re

with open("history_ui.py", "r") as f:
    code = f.read()

old_card_colors = """        fg = theme.get_color("text_primary")
        text_sec = theme.get_color("text_secondary")
        bg_hover = theme.get_color("bg_hover")
        accent = theme.get_color("accent")
        bg_input = theme.get_color("bg")"""

new_card_colors = """        fg = "white"
        text_sec = "#888"
        bg_hover = "#2a2a2a"
        accent = "#00FFFF"
        bg_input = "#1f1f23\"\"\""""
        
# Actually, let's just do direct replacements cleanly.
code = code.replace(old_card_colors, """        fg = "white"
        text_sec = "#888"
        bg_hover = "#2a2a2a"
        accent = "#00FFFF"
        bg_input = "#1f1f23\"\"\"""".replace('\"\"\"', ''))

old_main_colors = """        bg = theme.get_color("bg_sec")
        active = theme.get_color("bg_hover")
        border = theme.get_color("border")
        fg = theme.get_color("text_primary")
        text_sec = theme.get_color("text_secondary")
        bg_hover = theme.get_color("bg_hover")
        accent = theme.get_color("accent")
        bg_input = theme.get_color("bg")"""

code = code.replace(old_main_colors, """        bg = "#111"
        active = "#222"
        border = "#444"
        fg = "white"
        text_sec = "#888"
        bg_hover = "#2a2a2a"
        accent = "#00FFFF"
        bg_input = "#1f1f23\"\"\"""".replace('\"\"\"', ''))
        
code = code.replace('bg_panel = theme.get_color("bg_panel")', 'bg_panel = "#222"')

with open("history_ui.py", "w") as f:
    f.write(code)
