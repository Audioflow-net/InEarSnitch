import re

with open("main.py", "r") as f:
    code = f.read()

pattern_list = r'''        self\.list_targets = QListWidget\(\)
        self\.list_targets\.setStyleSheet\("background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 4px;"\)
        self\.list_targets\.setSelectionMode\(QAbstractItemView\.SingleSelection\)
        tgt_layout\.addWidget\(self\.list_targets\)'''

replacement_list = r'''        from PyQt5.QtWidgets import QLineEdit
        self.search_targets = QLineEdit()
        self.search_targets.setPlaceholderText("Search targets...")
        self.search_targets.setStyleSheet("background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 6px;")
        self.search_targets.textChanged.connect(self.filter_target_list)
        tgt_layout.addWidget(self.search_targets)
        
        self.list_targets = QListWidget()
        self.list_targets.setStyleSheet("background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 4px;")
        self.list_targets.setSelectionMode(QAbstractItemView.SingleSelection)
        tgt_layout.addWidget(self.list_targets)'''

code = re.sub(pattern_list, replacement_list, code)

pattern_method = r'''    def reload_target_list(self):'''

replacement_method = r'''    def filter_target_list(self, text):
        search_text = text.lower()
        for i in range(self.list_targets.count()):
            item = self.list_targets.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def reload_target_list(self):'''

code = code.replace(pattern_method, replacement_method)

with open("main.py", "w") as f:
    f.write(code)

print("Target Search patched.")
