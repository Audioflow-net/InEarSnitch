import re

with open('main.py', 'r') as f:
    content = f.read()

# Fix the raw newlines inside the string literal
# We look for the exact raw string block
bad_string = '        self.btn_live_seal = QPushButton("R\nT\nA")'
good_string = '        self.btn_live_seal = QPushButton("R\\nT\\nA")'

content = content.replace(bad_string, good_string)

with open('main.py', 'w') as f:
    f.write(content)
