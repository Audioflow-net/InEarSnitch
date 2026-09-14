import re

with open('theme.py', 'r') as f:
    content = f.read()

toggle_css = """
    QPushButton[class="chan_toggle"] {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_secondary')};
        border: 1px solid {get_color('border')};
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
    }}
    QPushButton[class="chan_toggle"]:hover {{
        background-color: {get_color('bg_hover')};
        color: {get_color('text_primary')};
        border: 1px solid {get_color('text_secondary')};
    }}
    QPushButton[class="chan_toggle"][chan="L"]:checked {{
        border: 2px solid #0ea5e9;
        color: #0ea5e9;
        background-color: transparent;
    }}
    QPushButton[class="chan_toggle"][chan="R"]:checked {{
        border: 2px solid #ef4444;
        color: #ef4444;
        background-color: transparent;
    }}
"""

if 'QPushButton[class="chan_toggle"]' not in content:
    # insert before QComboBox QAbstractItemView
    content = content.replace("    QComboBox QAbstractItemView {{", toggle_css + "\n    QComboBox QAbstractItemView {{")
    
    with open('theme.py', 'w') as f:
        f.write(content)
print("SUCCESS")
