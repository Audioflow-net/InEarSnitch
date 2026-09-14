import re

with open('main.py', 'r') as f:
    content = f.read()

content = content.replace('QPushButton("L\\nI\\nV\\nE")', 'QPushButton("R\\nT\\nA")')
content = content.replace('QPushButton("L\nI\nV\nE")', 'QPushButton("R\nT\nA")')

with open('main.py', 'w') as f:
    f.write(content)
