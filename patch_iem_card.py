import re

with open("profile_ui.py", "r") as f:
    code = f.read()

# 1. Update __init__
code = code.replace(
    'def __init__(self, iem_id, model_name, contact, notes, pic_path, abbr="", parent=None):',
    'def __init__(self, iem_id, model_name, contact, notes, pic_path, abbr="", custom_name="", parent=None):'
)

code = code.replace(
    'self.abbr = abbr or ""',
    'self.abbr = abbr or ""\n        self.custom_name = custom_name or ""'
)

# 2. Update title to use custom_name if available
code = code.replace(
    'self.lbl_title = QLabel(model_name or "Unknown IEM")',
    'display_name = f"{self.custom_name}\\n[{model_name}]" if self.custom_name else (model_name or "Unknown IEM")\n        self.lbl_title = QLabel(display_name)'
)

# 3. Add Custom Name input field to grid
grid_add = r'''        lbl_style = "color: #a1a1aa; font-size: 13px; font-weight: bold; background: transparent; border: none;"
        
        # Row 0: Custom Name
        l_name = QLabel("Name:"); l_name.setStyleSheet(lbl_style)
        from PyQt5.QtWidgets import QLineEdit
        self.custom_name_input = QLineEdit(self.custom_name)
        self.custom_name_input.setPlaceholderText("e.g. Ben's Main IEM")
        self.custom_name_input.setStyleSheet(f"background: transparent; border: none; border-bottom: 1px solid {bc}; color: {tc}; font-size: 14px; padding-bottom: 4px;")
        self.custom_name_input.textChanged.connect(self.sync_title)
        self.custom_name_input.textChanged.connect(self.data_changed.emit)
        grid.addWidget(l_name, 0, 0)
        grid.addWidget(self.custom_name_input, 0, 1, 1, 3)
        
        # Row 1: Model / Abbr'''

code = code.replace(
    '        lbl_style = "color: #a1a1aa; font-size: 13px; font-weight: bold; background: transparent; border: none;"\n        \n        # Row 0: Model / Abbr',
    grid_add
)

# Shift grid indices
code = code.replace('grid.addWidget(l_model, 0, 0)', 'grid.addWidget(l_model, 1, 0)')
code = code.replace('grid.addWidget(self.model_input, 0, 1)', 'grid.addWidget(self.model_input, 1, 1)')
code = code.replace('grid.addWidget(l_abbr, 0, 2)', 'grid.addWidget(l_abbr, 1, 2)')
code = code.replace('grid.addWidget(self.abbr_input, 0, 3)', 'grid.addWidget(self.abbr_input, 1, 3)')
code = code.replace('grid.addWidget(l_contact, 1, 0)', 'grid.addWidget(l_contact, 2, 0)')
code = code.replace('grid.addWidget(self.contact_input, 1, 1, 1, 3)', 'grid.addWidget(self.contact_input, 2, 1, 1, 3)')
code = code.replace('grid.addWidget(l_service, 2, 0)', 'grid.addWidget(l_service, 3, 0)')
code = code.replace('grid.addWidget(self.service_input, 2, 1, 1, 3)', 'grid.addWidget(self.service_input, 3, 1, 1, 3)')
code = code.replace('grid.addWidget(self.btn_select, 3, 0, 1, 4)', 'grid.addWidget(self.btn_select, 4, 0, 1, 4)')

# 4. Update sync_title
code = code.replace(
    '        val = self.model_input.currentText()',
    '        cname = self.custom_name_input.text().strip()\n        mname = self.model_input.currentText().strip()\n        val = f"{cname}\\n[{mname}]" if cname else (mname or "Unknown IEM")'
)

# 5. Update get_data
code = code.replace(
    "'model_name': self.model_input.currentText(),",
    "'model_name': self.model_input.currentText(),\n            'custom_name': self.custom_name_input.text(),"
)

# 6. Update ProfileEditorWidget.load_profile
code = code.replace(
    'SELECT id, model_name, contact_person, service_notes, iem_pic, abbreviation FROM IEM_Models',
    'SELECT id, model_name, contact_person, service_notes, iem_pic, abbreviation, custom_name FROM IEM_Models'
)
code = code.replace(
    '            for row in cursor.fetchall():\n                iem_id, model, contact, notes, pic, abbr = row',
    '            for row in cursor.fetchall():\n                iem_id, model, contact, notes, pic, abbr, cname = row'
)
code = code.replace(
    'card = IEMCardWidget(iem_id, model, contact, notes, pic, abbr)',
    'card = IEMCardWidget(iem_id, model, contact, notes, pic, abbr, cname)'
)

# 7. Update save_profile_data
code = code.replace(
    'SET model_name = ?, contact_person = ?, service_notes = ?, iem_pic = ?, abbreviation = ?',
    'SET model_name = ?, contact_person = ?, service_notes = ?, iem_pic = ?, abbreviation = ?, custom_name = ?'
)
code = code.replace(
    "data.get('abbr', ''), data['id']",
    "data.get('abbr', ''), data.get('custom_name', ''), data['id']"
)

# 8. Update add_iem
code = code.replace(
    'INSERT INTO IEM_Models (musician_id, model_name, contact_person, service_notes, iem_pic)',
    'INSERT INTO IEM_Models (musician_id, model_name, contact_person, service_notes, iem_pic, custom_name)'
)
code = code.replace(
    '(self.current_musician_id, "New IEM", "", "", "")',
    '(self.current_musician_id, "New IEM", "", "", "", "")'
)

with open("profile_ui.py", "w") as f:
    f.write(code)

print("profile_ui patched.")
