import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Remove the old db_group from set_layout
pattern_remove_db = r'''        # Database Management
        from PyQt5\.QtWidgets import QGroupBox
        db_group = QGroupBox\("Database Management"\)
        db_group\.setStyleSheet\("QGroupBox \{ color: #888; border: 1px solid #333; border-radius: 4px; margin-top: 10px; \} QGroupBox::title \{ subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; \}"\)
        db_layout = QHBoxLayout\(db_group\)
        
        btn_backup = QPushButton\("Backup Database"\)
        btn_backup\.setToolTip\("Create a safe backup copy of your entire database"\)
        btn_backup\.setStyleSheet\("QPushButton \{ background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 8px; font-weight: bold; \} QPushButton:hover \{ background-color: #3f3f46; \}"\)
        btn_backup\.clicked\.connect\(self\.backup_database\)
        db_layout\.addWidget\(btn_backup\)
        
        btn_restore = QPushButton\("Restore Database"\)
        btn_restore\.setToolTip\("Restore your database from a previously created backup"\)
        btn_restore\.setStyleSheet\("QPushButton \{ background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 8px; font-weight: bold; \} QPushButton:hover \{ background-color: #3f3f46; \}"\)
        btn_restore\.clicked\.connect\(self\.restore_database\)
        db_layout\.addWidget\(btn_restore\)
        
        set_layout\.addWidget\(db_group\)'''

code = re.sub(pattern_remove_db, '', code)

# 2. Add TAB 4: Database & Targets
pattern_add_tab = r'''        self\.settings_tabs\.addTab\(tab_manual, "Manual"\)'''
replacement_add_tab = r'''        self.settings_tabs.addTab(tab_manual, "Manual")

        # ── TAB 4: Database & Targets ───────────────────────────────────────
        tab_db = QWidget()
        tab_db.setStyleSheet("background: #222;")
        tab_db_layout = QVBoxLayout(tab_db)
        tab_db_layout.setSpacing(14)
        tab_db_layout.setContentsMargins(16, 16, 16, 16)
        
        # App Database
        from PyQt5.QtWidgets import QGroupBox, QListWidget, QAbstractItemView, QListWidgetItem
        db_group = QGroupBox("App Database (Profiles & Measurements)")
        db_group.setStyleSheet("QGroupBox { color: #888; border: 1px solid #333; border-radius: 4px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        db_layout = QHBoxLayout(db_group)
        
        btn_backup = QPushButton("Backup Database")
        btn_backup.setToolTip("Create a safe backup copy of your entire database")
        btn_backup.setStyleSheet("QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 8px; font-weight: bold; } QPushButton:hover { background-color: #3f3f46; }")
        btn_backup.clicked.connect(self.backup_database)
        db_layout.addWidget(btn_backup)
        
        btn_restore = QPushButton("Restore Database")
        btn_restore.setToolTip("Restore your database from a previously created backup")
        btn_restore.setStyleSheet("QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 8px; font-weight: bold; } QPushButton:hover { background-color: #3f3f46; }")
        btn_restore.clicked.connect(self.restore_database)
        db_layout.addWidget(btn_restore)
        
        tab_db_layout.addWidget(db_group)
        
        # Target Templates
        tgt_group = QGroupBox("Target Templates (Squiglink / Reference Curves)")
        tgt_group.setStyleSheet("QGroupBox { color: #888; border: 1px solid #333; border-radius: 4px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        tgt_layout = QVBoxLayout(tgt_group)
        
        self.list_targets = QListWidget()
        self.list_targets.setStyleSheet("background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 4px;")
        self.list_targets.setSelectionMode(QAbstractItemView.SingleSelection)
        tgt_layout.addWidget(self.list_targets)
        
        tgt_btn_row = QHBoxLayout()
        btn_import_tgt = QPushButton("Import CSV")
        btn_import_tgt.setStyleSheet("QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 6px; font-weight: bold; } QPushButton:hover { background-color: #3f3f46; }")
        btn_import_tgt.clicked.connect(self.import_target_template)
        tgt_btn_row.addWidget(btn_import_tgt)
        
        btn_export_tgt = QPushButton("Export Selected")
        btn_export_tgt.setStyleSheet("QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 6px; font-weight: bold; } QPushButton:hover { background-color: #3f3f46; }")
        btn_export_tgt.clicked.connect(self.export_target_template)
        tgt_btn_row.addWidget(btn_export_tgt)
        
        btn_delete_tgt = QPushButton("Delete Selected")
        btn_delete_tgt.setStyleSheet("QPushButton { background-color: #7f1d1d; color: white; border: 1px solid #991b1b; border-radius: 4px; padding: 6px; font-weight: bold; } QPushButton:hover { background-color: #991b1b; }")
        btn_delete_tgt.clicked.connect(self.delete_target_template)
        tgt_btn_row.addWidget(btn_delete_tgt)
        
        tgt_layout.addLayout(tgt_btn_row)
        tab_db_layout.addWidget(tgt_group)
        
        self.settings_tabs.addTab(tab_db, "Database & Targets")
        '''

code = re.sub(pattern_add_tab, replacement_add_tab, code)

# 3. Add the target methods
injection_methods = r'''    def reload_target_list(self):
        import os, glob
        if not hasattr(self, 'list_targets'): return
        self.list_targets.clear()
        target_dir = os.path.join("reference_targets", "Pro_Live_IEMs")
        if os.path.exists(target_dir):
            files = glob.glob(os.path.join(target_dir, "*.csv"))
            for f in sorted(files):
                from PyQt5.QtWidgets import QListWidgetItem
                name = os.path.basename(f)
                item = QListWidgetItem(name)
                item.setData(100, f)
                self.list_targets.addItem(item)
                
    def import_target_template(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import os
        paths, _ = QFileDialog.getOpenFileNames(self, "Import Target CSV(s)", "", "CSV Files (*.csv)")
        if not paths: return
        target_dir = os.path.join("reference_targets", "Pro_Live_IEMs")
        os.makedirs(target_dir, exist_ok=True)
        imported = 0
        try:
            for path in paths:
                filename = os.path.basename(path)
                shutil.copy2(path, os.path.join(target_dir, filename))
                imported += 1
            QMessageBox.information(self, "Success", f"Imported {imported} target(s).")
            self.reload_target_list()
            self.load_targets()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import: {e}")

    def export_target_template(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import os
        item = self.list_targets.currentItem()
        if not item:
            QMessageBox.warning(self, "Export", "Select a target to export.")
            return
        src_path = item.data(100)
        filename = os.path.basename(src_path)
        dst_path, _ = QFileDialog.getSaveFileName(self, "Export Target", filename, "CSV Files (*.csv)")
        if not dst_path: return
        try:
            shutil.copy2(src_path, dst_path)
            QMessageBox.information(self, "Success", "Target exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

    def delete_target_template(self):
        from PyQt5.QtWidgets import QMessageBox
        import os
        item = self.list_targets.currentItem()
        if not item:
            QMessageBox.warning(self, "Delete", "Select a target to delete.")
            return
        src_path = item.data(100)
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{os.path.basename(src_path)}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(src_path)
                self.reload_target_list()
                self.load_targets()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

    def backup_database(self):'''

code = code.replace('    def backup_database(self):', injection_methods)

# Call reload_target_list after self.load_targets() in setup_ui
code = code.replace('self.load_targets()', 'self.load_targets()\n        self.reload_target_list()', 1)

with open("main.py", "w") as f:
    f.write(code)

print("Settings tabs patched.")
