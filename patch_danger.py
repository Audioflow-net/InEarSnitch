with open('theme.py', 'r') as f:
    content = f.read()

danger_disabled = """
    QPushButton[class="danger"]:disabled {{
        background-color: {get_color('bg_hover')};
        color: {get_color('text_secondary')};
    }}
"""

if "QPushButton[class=\"danger\"]:disabled" not in content:
    content = content.replace(
        'QPushButton[class="danger"]:hover {{',
        danger_disabled + '\n    QPushButton[class="danger"]:hover {{'
    )
    with open('theme.py', 'w') as f:
        f.write(content)
    print("SUCCESS")
