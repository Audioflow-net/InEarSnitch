import sqlite3
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class AddProfileDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add Musician & IEM")
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: white; }
            QLabel { color: #ccc; }
            QLineEdit { background-color: #111; color: white; border: 1px solid #333; padding: 5px; border-radius: 4px; }
            QPushButton { background-color: #00FFFF; color: black; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #00cccc; }
            QPushButton#cancelBtn { background-color: #444; color: white; }
            QPushButton#cancelBtn:hover { background-color: #555; }
        """)
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Liam O'Connell")
        layout.addWidget(QLabel("Musician Name:"))
        layout.addWidget(self.name_input)
        
        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("e.g. Vocals")
        layout.addWidget(QLabel("Role/Band:"))
        layout.addWidget(self.role_input)
        
        self.iem_input = QLineEdit()
        self.iem_input.setPlaceholderText("e.g. SE846")
        layout.addWidget(QLabel("IEM Model:"))
        layout.addWidget(self.iem_input)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Profile")
        save_btn.clicked.connect(self.save_profile)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def save_profile(self):
        name = self.name_input.text().strip()
        role = self.role_input.text().strip()
        iem = self.iem_input.text().strip()
        
        if not name or not iem:
            QMessageBox.warning(self, "Validation Error", "Name and IEM Model are required.")
            return
            
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Insert Musician
            cursor.execute("INSERT INTO Musicians (name, band) VALUES (?, ?)", (name, role))
            musician_id = cursor.lastrowid
            
            # Insert IEM
            cursor.execute("INSERT INTO IEM_Models (musician_id, model_name) VALUES (?, ?)", (musician_id, iem))
            
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
