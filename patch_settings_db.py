import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''        # Save button – no popup, no panel close; inline feedback only'''

replacement = r'''        # Database Management
        db_group = QGroupBox("Database Management")
        db_group.setStyleSheet("QGroupBox { color: #888; border: 1px solid #333; border-radius: 4px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        db_layout = QHBoxLayout(db_group)
        
        btn_backup = QPushButton("Backup Database")
        btn_backup.setStyleSheet("QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 8px; font-weight: bold; } QPushButton:hover { background-color: #3f3f46; }")
        btn_backup.clicked.connect(self.backup_database)
        db_layout.addWidget(btn_backup)
        
        btn_restore = QPushButton("Restore Database")
        btn_restore.setStyleSheet("QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 8px; font-weight: bold; } QPushButton:hover { background-color: #3f3f46; }")
        btn_restore.clicked.connect(self.restore_database)
        db_layout.addWidget(btn_restore)
        
        set_layout.addWidget(db_group)

        # Save button – no popup, no panel close; inline feedback only'''

code = code.replace(pattern, replacement)

injection = r'''    def backup_database(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import datetime
        import os
        
        default_name = f"inearsnitch_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.db"
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", default_name, "SQLite Database (*.db)")
        if not path: return
        
        try:
            shutil.copy2(self.db.db_path, path)
            QMessageBox.information(self, "Backup Success", f"Database successfully backed up to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to backup database:\n{e}")

    def restore_database(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import os
        
        QMessageBox.warning(self, "Restore Database", "Restoring a database will OVERWRITE all current profiles and measurements!\n\nA temporary backup of your current database will be created just in case.")
        
        path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database (*.db)")
        if not path: return
        
        try:
            # Create a safety backup of the current DB
            safety_path = self.db.db_path + ".safety.bak"
            if os.path.exists(self.db.db_path):
                shutil.copy2(self.db.db_path, safety_path)
                
            # Overwrite with the selected file
            shutil.copy2(path, self.db.db_path)
            
            QMessageBox.information(self, "Restore Success", "Database successfully restored!\n\nThe application will now reload your profiles.")
            
            # Reload application state
            self.current_iem_id = None
            self.current_musician_name = None
            self.current_iem_name = None
            self.update_watermark()
            self.load_profiles_from_db()
            self.load_targets()
            
            if hasattr(self, 'page_hist') and hasattr(self.page_hist, 'table'):
                self.page_hist.table.setRowCount(0)
                
            self.switch_workspace_tab(0) # Go to profiles tab
            
        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"Failed to restore database:\n{e}")

    def save_settings(self):'''

code = code.replace('    def save_settings(self):', injection)

with open("main.py", "w") as f:
    f.write(code)

print("Settings patched.")
