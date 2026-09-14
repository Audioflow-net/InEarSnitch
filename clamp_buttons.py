import sys

with open('main.py', 'r') as f:
    content = f.read()

# Change btn_capture to Fixed vertical
content = content.replace('self.btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)', 'self.btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)\n        self.btn_capture.setMinimumHeight(60)')

# Change btn_live_seal to Fixed vertical
content = content.replace('self.btn_live_seal.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)', 'self.btn_live_seal.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)\n        self.btn_live_seal.setMinimumHeight(60)')

with open('main.py', 'w') as f:
    f.write(content)
