import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Inject class ProKitTipSelector
class_code = """
class ProKitTipSelector(QPushButton):
    currentIndexChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cb_prokit_tip")
        self.setToolTip("Select ProKit Coupler Ear Tip")
        self.setCursor(Qt.PointingHandCursor)
        self.items = []
        self._current_index = -1
        self._signals_blocked = False
        self.clicked.connect(self.show_popup)
        self.update_styling()
        
    def blockSignals(self, b):
        self._signals_blocked = b
        return super().blockSignals(b)
        
    def update_styling(self):
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        hover = theme.get_color('accent_edge')
        self.setStyleSheet(f\"\"\"
            QPushButton {{
                background-color: {bg};
                color: {fg};
                font-weight: bold;
                font-size: 12px;
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                border: 1px solid {hover};
            }}
        \"\"\")
        
    def clear(self):
        self.items = []
        self._current_index = -1
        self.setText("Select Tip...  ▼")
        
    def addItem(self, text, userData=None):
        self.items.append({'text': text, 'data': userData})
        if self._current_index == -1:
            self.setCurrentIndex(0)
            
    def count(self):
        return len(self.items)
        
    def currentData(self):
        if 0 <= self._current_index < len(self.items):
            return self.items[self._current_index]['data']
        return None
        
    def findData(self, data):
        for i, item in enumerate(self.items):
            if item['data'] == data:
                return i
        return -1
        
    def setCurrentIndex(self, idx):
        if 0 <= idx < len(self.items):
            self._current_index = idx
            self.setText(self.items[idx]['text'] + "  ▼")
            if not self._signals_blocked:
                self.currentIndexChanged.emit(idx)
                
    def show_popup(self):
        from PySide6.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QWidget, QLabel
        dialog = QDialog(self.window())
        dialog.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        
        main_widget = QWidget(dialog)
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        hover = theme.get_color('bg_hover')
        
        main_widget.setStyleSheet(f\"\"\"
            QWidget#PopupMain {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                color: {fg};
            }}
            QPushButton:hover {{
                background-color: {hover};
                border: 1px solid {border};
            }}
        \"\"\")
        main_widget.setObjectName("PopupMain")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(main_widget)
        
        grid = QGridLayout(main_widget)
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("Select Ear Tip")
        title.setStyleSheet(f"font-weight: 900; font-size: 14px; color: {fg}; padding-bottom: 5px; border: none; background: transparent;")
        grid.addWidget(title, 0, 0, 1, 4)
        
        row, col = 1, 0
        for i, item in enumerate(self.items):
            btn = QPushButton()
            btn.setFixedSize(90, 90)
            btn.setCursor(Qt.PointingHandCursor)
            
            parts = item['text'].split(' ', 1)
            icon = parts[0] if len(parts) > 1 else ""
            name = parts[1] if len(parts) > 1 else item['text']
            
            btn_layout = QVBoxLayout(btn)
            btn_layout.setSpacing(4)
            
            lbl_icon = QLabel(icon)
            lbl_icon.setAlignment(Qt.AlignCenter)
            lbl_icon.setStyleSheet("font-size: 32px; color: #0ea5e9; border: none; background: transparent;")
            
            lbl_name = QLabel(name)
            lbl_name.setAlignment(Qt.AlignCenter)
            lbl_name.setWordWrap(True)
            lbl_name.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {fg}; border: none; background: transparent;")
            
            btn_layout.addWidget(lbl_icon)
            btn_layout.addWidget(lbl_name)
            
            def make_handler(idx):
                def handler(checked):
                    self.setCurrentIndex(idx)
                    dialog.accept()
                return handler
            btn.clicked.connect(make_handler(i))
            
            if i == self._current_index:
                btn.setStyleSheet(f\"\"\"
                    QPushButton {{
                        background-color: {theme.get_color('accent_glow')};
                        border: 1px solid {theme.get_color('accent_edge')};
                        border-radius: 8px;
                        color: {fg};
                    }}
                \"\"\")
            
            grid.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        pos = self.mapToGlobal(self.rect().topLeft())
        dialog.adjustSize()
        dialog.move(pos.x(), pos.y() - dialog.height() - 5)
        dialog.exec()

class MainWindow(QMainWindow):
"""

content = content.replace("class MainWindow(QMainWindow):", class_code)

# 2. Replace QComboBox
old_setup = """        # --- PROKIT EAR TIP SELECTOR (next to L/R) ---
        self.combo_tip = QComboBox()
        self.combo_tip.setObjectName("cb_prokit_tip")
        self.combo_tip.setEditable(False)
        self.combo_tip.setMinimumWidth(100)
        self.combo_tip.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.combo_tip.setToolTip("Select ProKit Coupler Ear Tip")
        self.combo_tip.setStyleSheet(\"\"\"
            QComboBox {
                background-color: #222;
                color: #e4e4e7;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                border-color: #10b981;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #222;
                color: #e4e4e7;
                selection-background-color: #10b981;
                selection-color: black;
                border: 1px solid #444;
                min-width: 180px;
            }
        \"\"\")"""

new_setup = """        # --- PROKIT EAR TIP SELECTOR (next to L/R) ---
        self.combo_tip = ProKitTipSelector(self)"""

content = content.replace(old_setup, new_setup)

with open("main.py", "w") as f:
    f.write(content)
