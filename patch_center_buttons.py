with open('theme.py', 'r') as f:
    content = f.read()

center_buttons_style = """
    QDialogButtonBox {
        qproperty-centerButtons: true;
    }
"""

if "QDialogButtonBox {" not in content:
    content = content.replace('    QMessageBox {', center_buttons_style + '\n    QMessageBox {')
    with open('theme.py', 'w') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("ALREADY EXISTS")
