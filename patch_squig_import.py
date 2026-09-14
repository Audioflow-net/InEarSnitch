import re

with open('main.py', 'r') as f:
    content = f.read()

content = content.replace('"CSV Files (*.csv)")', '"CSV (*.csv *.txt)")')

with open('main.py', 'w') as f:
    f.write(content)
