with open('theme.py', 'r') as f:
    content = f.read()

combo_view_style = """
    QComboBox QAbstractItemView {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
        selection-background-color: {get_color('accent')};
        selection-color: white;
        border: 1px solid {get_color('border')};
        outline: none;
    }}
"""

if "QComboBox QAbstractItemView" not in content:
    content = content.replace(
        '    QListWidget, QScrollArea, QComboBox {{',
        combo_view_style + '\n    QListWidget, QScrollArea, QComboBox {{'
    )
    with open('theme.py', 'w') as f:
        f.write(content)
    print("SUCCESS")
