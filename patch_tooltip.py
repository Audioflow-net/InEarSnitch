with open('theme.py', 'r') as f:
    content = f.read()

tooltip_style = """
    QToolTip {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
        border: 1px solid {get_color('border')};
        padding: 4px;
        border-radius: 4px;
        font-size: 11px;
    }}
"""

if "QToolTip" not in content:
    content = content.replace('    QLabel {{', tooltip_style + '\n    QLabel {{')
    with open('theme.py', 'w') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("ALREADY EXISTS")
