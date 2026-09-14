import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Change self.layout to QHBoxLayout and remove splitter
old_layout_init = r"""        self\.layout = QVBoxLayout\(self\)
        self\.layout\.setContentsMargins\(0,0,0,0\)
        
        
        # --- Splitter ---
        self\.splitter = QSplitter\(Qt\.Vertical\)
        self\.layout\.addWidget\(self\.splitter\)
        
        # TOP of splitter: Graph
        wrapper = QWidget\(\)
        wrap_layout = QHBoxLayout\(wrapper\)
        wrap_layout\.setContentsMargins\(4, 4, 4, 4\)
        wrap_layout\.setSpacing\(6\)"""

new_layout_init = """        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(6)"""
        
code = re.sub(old_layout_init, new_layout_init, code)

# 2. Replace wrap_layout.addWidget(self.graph_tabs) with self.layout.addWidget
code = code.replace("wrap_layout.addWidget(self.graph_tabs, stretch=1)", "self.layout.addWidget(self.graph_tabs, stretch=1)")

# 3. Restructure tools_tabs and add table to it
# Remove lbl_targets_info
old_tools = r"""        lbl_targets_info = QLabel\("Select a measurement below to manage it or save it as a Reference Target\."\)
        lbl_targets_info\.setWordWrap\(True\)
        lbl_targets_info\.setStyleSheet\("color: #888; font-size: 12px; margin-bottom: 20px;"\)
        target_layout\.addWidget\(lbl_targets_info\)
        
        # --- MOVE BUTTONS HERE ---"""

new_tools = """        # The table goes here!
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "IEM", "Side", "Notes", "Graph"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.itemSelectionChanged.connect(self.on_item_selected)
        self.table.verticalHeader().setVisible(False)
        target_layout.addWidget(self.table, stretch=1)
        
        # --- BUTTONS ---
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(6)"""
        
code = re.sub(old_tools, new_tools, code)

# Fix button additions to use btn_layout
code = code.replace("target_layout.addWidget(self.btn_import_history)", "btn_layout.addWidget(self.btn_import_history)")
code = code.replace("target_layout.addWidget(self.btn_save_target)", "btn_layout.addWidget(self.btn_save_target)")
code = code.replace("target_layout.addWidget(self.btn_export_history)", "btn_layout.addWidget(self.btn_export_history)")
code = code.replace("target_layout.addWidget(self.btn_delete_history)", "btn_layout.addWidget(self.btn_delete_history)")

code = code.replace("target_layout.addStretch()", "target_layout.addLayout(btn_layout)")

# Rename "Targets" tab to "Measurements" if desired, or keep "Targets"
code = code.replace('self.tools_tabs.addTab(target_tab, "Targets")', 'self.tools_tabs.addTab(target_tab, "Measurements")')
code = code.replace('wrap_layout.addWidget(self.tools_tabs)', 'self.layout.addWidget(self.tools_tabs)')

# 4. Remove all the old splitter, bottom_container, and table setup code
old_bottom = r"""        self\.splitter\.addWidget\(wrapper\)
        
        # BOTTOM of splitter: Table \+ Inspector
        bottom_container = QWidget\(\)
        bottom_layout = QHBoxLayout\(bottom_container\)
        bottom_layout\.setContentsMargins\(0, 0, 0, 0\)
        bottom_layout\.setSpacing\(15\)
        
        # Left side: Table \+ Buttons
        table_container = QWidget\(\)
        table_layout = QVBoxLayout\(table_container\)
        table_layout\.setContentsMargins\(0, 0, 0, 0\)
        

        
        self\.table = QTableWidget\(\)
        self\.table\.setColumnCount\(5\)
        self\.table\.setHorizontalHeaderLabels\(\["Date", "IEM", "Side", "Notes", "Graph"\]\)
        
        header = self\.table\.horizontalHeader\(\)
        header\.setSectionResizeMode\(0, QHeaderView\.ResizeToContents\)
        header\.setSectionResizeMode\(1, QHeaderView\.ResizeToContents\)
        header\.setSectionResizeMode\(2, QHeaderView\.ResizeToContents\)
        header\.setSectionResizeMode\(3, QHeaderView\.Stretch\)
        header\.setSectionResizeMode\(4, QHeaderView\.ResizeToContents\)
        
        
        self\.table\.setSelectionBehavior\(QAbstractItemView\.SelectRows\)
        self\.table\.setSelectionMode\(QAbstractItemView\.SingleSelection\)
        self\.table\.setEditTriggers\(QAbstractItemView\.DoubleClicked \| QAbstractItemView\.EditKeyPressed\)
        self\.table\.itemChanged\.connect\(self\.on_item_changed\)
        self\.table\.itemSelectionChanged\.connect\(self\.on_item_selected\)
        self\.table\.verticalHeader\(\)\.setVisible\(False\)
        table_layout\.addWidget\(self\.table\)
        
        bottom_layout\.addWidget\(table_container, stretch=2\)
        

        
        self\.splitter\.addWidget\(bottom_container\)
        self\.splitter\.setSizes\(\[450, 250\]\)"""

code = re.sub(old_bottom, "", code)

# 5. target_layout margins should probably be much smaller so the table fits well
code = code.replace("target_layout.setContentsMargins(15, 15, 15, 15)", "target_layout.setContentsMargins(4, 4, 4, 4)")

with open("history_ui.py", "w") as f:
    f.write(code)
print("SUCCESS")
