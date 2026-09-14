with open('theme.py', 'r') as f:
    content = f.read()

msgbox_style = """
    QMessageBox {
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
    }
    QMessageBox QLabel {
        color: {get_color('text_primary')};
        background-color: transparent;
    }
    QMessageBox QPushButton {
        background-color: {get_color('bg_hover')};
        color: {get_color('text_primary')};
        border: 1px solid {get_color('border')};
        padding: 5px 15px;
        border-radius: 4px;
    }
    QMessageBox QPushButton:hover {
        border: 1px solid {get_color('accent')};
    }
"""

if "QMessageBox {" not in content:
    content = content.replace('    QLabel {', msgbox_style + '\n    QLabel {')
    with open('theme.py', 'w') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("ALREADY EXISTS")
