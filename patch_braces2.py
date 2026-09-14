with open('theme.py', 'r') as f:
    content = f.read()

content = content.replace(
"""    QDialogButtonBox {
        qproperty-centerButtons: true;
    }""",
"""    QDialogButtonBox {{
        qproperty-centerButtons: true;
    }}"""
)

with open('theme.py', 'w') as f:
    f.write(content)
print("SUCCESS")
