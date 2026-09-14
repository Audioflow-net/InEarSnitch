import re

with open('theme.py', 'r') as f:
    content = f.read()

new_css = """
    #musicianCardObj {{
        background-color: {get_color('bg_panel')};
        border-radius: 8px;
        border: 1px solid transparent;
        outline: none;
    }}
    #musicianCardObj[selected="true"] {{
        background-color: {get_color('bg_hover')};
        border-left: 4px solid {get_color('accent')};
        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
    }}
    
    QLabel[class="avatar_btn"] {{
        background-color: {get_color('bg_panel')};
        border: 2px solid {get_color('border')};
        border-radius: 18px;
        color: {get_color('text_secondary')};
        font-size: 14px;
        font-weight: bold;
    }}
    QLabel[class="avatar_btn"]:hover {{
        background-color: {get_color('bg_hover')};
        border: 2px solid {get_color('text_secondary')};
        color: {get_color('text_primary')};
    }}
    QLabel[class="avatar_btn"][selected="true"] {{
        background-color: {get_color('accent')};
        color: #000000;
        border: 2px solid {get_color('accent')};
    }}
    
    QLabel[class="avatar_btn_pic"] {{
        background-color: transparent;
        border: 2px solid {get_color('border')};
        border-radius: 18px;
        color: {get_color('text_secondary')};
        font-size: 14px;
        font-weight: bold;
    }}
    QLabel[class="avatar_btn_pic"]:hover {{
        background-color: transparent;
        border: 2px solid {get_color('text_secondary')};
    }}
    QLabel[class="avatar_btn_pic"][selected="true"] {{
        background-color: transparent;
        border: 2px solid {get_color('accent')};
    }}
"""

content = re.sub(
    r'\s*QLabel\[class="avatar_btn"\].*?border: 2px solid \{get_color\(\'accent\'\)\};\s*\}\}',
    new_css,
    content,
    flags=re.DOTALL
)

with open('theme.py', 'w') as f:
    f.write(content)
print("SUCCESS")
