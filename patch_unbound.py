import sys

with open('metrology_lab.py', 'r') as f:
    content = f.read()

content = content.replace("from PyQt5.QtGui import QPolygonF, QColor", "from PyQt5.QtGui import QPolygonF")

with open('metrology_lab.py', 'w') as f:
    f.write(content)
