import os
import sqlite3
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QFormLayout, 
                             QTextEdit, QFileDialog, QInputDialog, QGridLayout, 
                             QSizePolicy, QScrollArea, QMessageBox)
from PySide6.QtCore import Signal, Property, QTimer, QPropertyAnimation, QEasingCurve, Qt, QSize
from flow_layout import FlowLayout
from PySide6.QtGui import QPixmap, QImageReader, QPainter, QPainterPath

def create_circular_pixmap(image_reader, size):
    # Optimize decoding by reading only the necessary resolution!
    # A 12-Megapixel image doesn't need to be fully decoded just to make a 100x100 thumbnail.
    image_reader.setAutoTransform(True)
    orig_size = image_reader.size()
    if not orig_size.isEmpty():
        # Calculate scale down to save massive amounts of CPU/RAM
        min_dim = min(orig_size.width(), orig_size.height())
        if min_dim > size * 2: # Keep 2x resolution for retina/anti-aliasing before crop
            scale_factor = (size * 2) / min_dim
            new_w = int(orig_size.width() * scale_factor)
            new_h = int(orig_size.height() * scale_factor)
            image_reader.setScaledSize(QSize(new_w, new_h))
            
    img = image_reader.read()
    if img.isNull():
        return None
        
    w = img.width()
    h = img.height()
    
    # 1. Crop to a perfect square. 
    min_dim = min(w, h)
    x_offset = (w - min_dim) // 2
    if h > w:
        y_offset = int((h - min_dim) * 0.2)
    else:
        y_offset = (h - min_dim) // 2
        
    square_img = img.copy(x_offset, y_offset, min_dim, min_dim)
    
    # 2. Scale exactly to target size
    scaled_img = square_img.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # 3. Create a transparent pixmap and draw a circle
    target = QPixmap(size, size)
    target.fill(Qt.transparent)
    
    painter = QPainter(target)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    
    painter.drawPixmap(0, 0, QPixmap.fromImage(scaled_img))
    painter.end()
    
    return target



class ProfilePicWidget(QWidget):
    clicked = Signal()
    
    def __init__(self, size=120, placeholder="Upload", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.placeholder = placeholder
        self.has_image = False
        self.current_pic_path = ""
        
        self.img_label = QLabel(self)
        self.img_label.setAlignment(Qt.AlignCenter)
        
        self.overlay = QLabel(self)
        self.overlay.setAlignment(Qt.AlignCenter)
        self.overlay.setText("Change")
        self.overlay.hide()
        
        self.set_size(size)
        
    def set_size(self, size):
        self.size_val = size
        self.setFixedSize(size, size)
        self.img_label.setFixedSize(size, size)
        self.overlay.setFixedSize(size, size)
        
        font_size = max(9, int(size * 0.12))
        self.overlay.setStyleSheet(f"background-color: rgba(0, 0, 0, 160); border-radius: {size//2}px; color: white; font-weight: bold; font-size: {font_size}px;")
        
        if self.has_image and self.current_pic_path:
            self.refresh_image()
        else:
            self.set_empty_style()
            
    def refresh_image(self):
        if not self.current_pic_path or not os.path.exists(self.current_pic_path):
            self.set_image(None)
            return
        reader = QImageReader(self.current_pic_path)
        reader.setAutoTransform(True)
        circ_pix = create_circular_pixmap(reader, self.size_val)
        
        self.img_label.setPixmap(circ_pix)
        self.img_label.setStyleSheet("background-color: transparent; border: none;")
        self.has_image = True

    def set_empty_style(self):
        font_size = max(9, int(self.size_val * 0.12))
        self.img_label.setPixmap(QPixmap())
        self.img_label.setText(self.placeholder)
        self.img_label.setStyleSheet(f"background-color: transparent; border-radius: {self.size_val//2}px; border: 1px dashed #555; color: #888; font-size: {font_size}px;")
        self.has_image = False

    def set_image(self, pic_path):
        self.current_pic_path = pic_path
        if pic_path:
            self.has_image = True
            self.refresh_image()
        else:
            self.has_image = False
            self.set_empty_style()
            
    def enterEvent(self, event):
        self.overlay.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.overlay.hide()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class IEMCardWidget(QFrame):
    delete_requested = Signal(int)
    expanded_state_changed = Signal()
    data_changed = Signal()
    load_requested = Signal(int)
    
    def __init__(self, iem_id, model_name, contact, notes, pic_path, abbr="", custom_name="", color="#2a2a2a", parent=None):
        super().__init__(parent)
        self.iem_id = iem_id
        self.pic_path = pic_path or ""
        self.abbr = abbr or ""
        self.custom_name = custom_name or ""
        self.iem_color = color or "#2a2a2a"
        self.setProperty("class", "iem-card")
        self.expanded = False
        self.setObjectName("IemCardObj")
        self.setFixedHeight(260)
        
        import theme
        if theme.CURRENT_MODE == "light":
            self.setStyleSheet("#IemCardObj { background-color: #ffffff; border-radius: 8px; border: none; outline: none; }")
        else:
            self.setStyleSheet("#IemCardObj { background-color: #2d2d34; border-radius: 8px; border: none; outline: none; }")
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- LEFT: Avatar ---
        self.avatar_container = QFrame()
        self.avatar_container.setStyleSheet("background-color: transparent; border: none;")
        self.avatar_container.setMinimumWidth(150)
        self.avatar_container.setCursor(Qt.PointingHandCursor)
        self.avatar_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.avatar_layout = QVBoxLayout(self.avatar_container)
        self.avatar_layout.setContentsMargins(20, 20, 20, 20)
        self.avatar_layout.setAlignment(Qt.AlignCenter)
        
        self.pic_widget = ProfilePicWidget(size=100, placeholder="Add Photo")
        self.pic_widget.clicked.connect(self.handle_pic_click)
        self.pic_widget.set_image(self.pic_path)
        self.avatar_layout.addWidget(self.pic_widget, alignment=Qt.AlignCenter)
        
        display_name = f"{self.custom_name}\n[{model_name}]" if self.custom_name else (model_name or "Unknown IEM")
        self.lbl_title = QLabel(display_name)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("background-color: transparent; color: white; font-weight: bold; font-size: 14px; margin-top: 5px; border: none; outline: none;")
        self.lbl_title.setWordWrap(True)
        self.avatar_layout.addWidget(self.lbl_title)
        
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 5, 0, 0)
        btn_layout.setSpacing(5)
        
        self.btn_pick_color = QPushButton("Color")
        self.btn_pick_color.setStyleSheet("QPushButton { background-color: #333; color: white; border-radius: 4px; padding: 4px 8px; font-size: 10px; } QPushButton:hover { background-color: #444; }")
        self.btn_pick_color.setCursor(Qt.PointingHandCursor)
        self.btn_pick_color.clicked.connect(self.choose_color)
        btn_layout.addWidget(self.btn_pick_color)
        
        self.btn_remove_pic = QPushButton("Remove")
        self.btn_remove_pic.setStyleSheet("QPushButton { background-color: #500; color: white; border-radius: 4px; padding: 4px 8px; font-size: 10px; } QPushButton:hover { background-color: #700; }")
        self.btn_remove_pic.setCursor(Qt.PointingHandCursor)
        self.btn_remove_pic.clicked.connect(self.remove_pic)
        btn_layout.addWidget(self.btn_remove_pic)
        
        self.avatar_layout.addLayout(btn_layout)
        
        # Initial color application
        self.apply_color()
        
        self.main_layout.addWidget(self.avatar_container)
        
        # --- RIGHT: Form (Grid Layout) ---
        self.form_container = QFrame()
        self.form_container.setStyleSheet("background-color: transparent; border: none;")
        self.form_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(15, 20, 25, 20)
        self.form_layout.setSpacing(20)
        
        from PySide6.QtWidgets import QComboBox, QCompleter, QGridLayout

        # Clean Header Layout (Title + Delete Button)
        header_h = QHBoxLayout()
        title_lbl = QLabel("IEM Settings")
        title_lbl.setStyleSheet("color: #0ea5e9; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        header_h.addWidget(title_lbl)
        header_h.addStretch()
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setToolTip("Delete this item")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setStyleSheet('''
            QPushButton { background-color: transparent; border: 1px solid #ef4444; color: #ef4444; border-radius: 4px; padding: 4px 12px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: rgba(239, 68, 68, 0.1); }
        ''')
        self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.iem_id))
        
        self.btn_done = QPushButton("Done")
        self.btn_done.setToolTip("Save changes and finish editing")
        self.btn_done.setCursor(Qt.PointingHandCursor)
        self.btn_done.setStyleSheet('''
            QPushButton { background-color: transparent; border: 1px solid #0ea5e9; color: #0ea5e9; border-radius: 4px; padding: 4px 12px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: rgba(14, 165, 233, 0.1); }
        ''')
        self.btn_done.clicked.connect(self.toggle_expand)
        
        header_h.addWidget(self.btn_done)
        header_h.addWidget(self.btn_delete)
        self.form_layout.addLayout(header_h)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        lbl_style = "color: #a1a1aa; font-size: 13px; font-weight: bold; background: transparent; border: none;"

        import theme
        tc = theme.get_color('text_primary')
        bc = theme.get_color('border')
        bg = theme.get_color('bg_secondary')
        
        # Row 0: Custom Name
        l_name = QLabel("Name:"); l_name.setStyleSheet(lbl_style)
        from PySide6.QtWidgets import QLineEdit
        self.custom_name_input = QLineEdit(self.custom_name)
        self.custom_name_input.setPlaceholderText("e.g. Ben's Main IEM")
        self.custom_name_input.setStyleSheet(f"background: transparent; border: none; border-bottom: 1px solid {bc}; color: {tc}; font-size: 14px; padding-bottom: 4px;")
        self.custom_name_input.textChanged.connect(self.sync_title)
        self.custom_name_input.textChanged.connect(self.data_changed.emit)
        grid.addWidget(l_name, 0, 0)
        grid.addWidget(self.custom_name_input, 0, 1, 1, 3)
        
        # Row 1: Model / Abbr
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        

        self.model_input.setStyleSheet(f"""
            QComboBox {{ background: transparent; border: none; border-bottom: 1px solid {bc}; color: {tc}; font-size: 14px; padding-bottom: 4px; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{ width: 0; height: 0; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid {tc}; margin-right: 8px; }}
            QComboBox QAbstractItemView {{ background: {bg}; color: {tc}; border: 1px solid {bc}; }}
        """)

        models = set()
        import sqlite3, os, glob
        if os.path.exists("inearsnitch.db"):
            try:
                conn = sqlite3.connect("inearsnitch.db")
                c = conn.cursor()
                c.execute("SELECT DISTINCT model_name FROM IEM_Models WHERE model_name IS NOT NULL AND model_name != ''")
                for row in c.fetchall(): models.add(row[0])
                conn.close()
            except: pass
        if os.path.exists("reference_targets"):
            for path in glob.glob(os.path.join("reference_targets", "**/*.csv"), recursive=True):
                name = os.path.basename(path).replace(".csv", "").replace(".txt", "").replace("_", " ")
                name = name.replace(" Reference", "").replace(" Pristine", "").strip()
                models.add(name)
        self.model_input.addItems(sorted(list(models)))
        self.model_input.setCurrentText(model_name)
        
        completer = self.model_input.completer()
        if completer:
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            
        line_edit = self.model_input.lineEdit()
        def on_mouse_press(event, le=line_edit):
            from PySide6.QtWidgets import QLineEdit
            QLineEdit.mousePressEvent(le, event)
            le.selectAll()
        line_edit.mousePressEvent = on_mouse_press
        try:
            line_edit.editingFinished.connect(self.sync_title)
            line_edit.textChanged.connect(self.data_changed.emit)
        except Exception:
            pass

        l_model = QLabel("Model:"); l_model.setStyleSheet(lbl_style)
        grid.addWidget(l_model, 1, 0)
        grid.addWidget(self.model_input, 1, 1)
        
        self.abbr_input = QLineEdit(abbr)
        self.abbr_input.setPlaceholderText("Abbr.")
        self.abbr_input.setProperty("class", "prof_clean_input")
        self.abbr_input.textChanged.connect(self.data_changed.emit)
        self.abbr_input.textChanged.connect(self.sync_title)
        
        l_abbr = QLabel("Abbr:"); l_abbr.setStyleSheet(lbl_style)
        grid.addWidget(l_abbr, 1, 2)
        grid.addWidget(self.abbr_input, 1, 3)
        
        # Row 1: Contact
        self.contact_input = QLineEdit(contact or "")
        self.contact_input.setPlaceholderText("Contact Person / Tech")
        self.contact_input.setProperty("class", "prof_clean_input")
        self.contact_input.textChanged.connect(self.data_changed.emit)
        l_contact = QLabel("Contact:"); l_contact.setStyleSheet(lbl_style)
        grid.addWidget(l_contact, 2, 0)
        grid.addWidget(self.contact_input, 2, 1, 1, 3)
        
        # Row 2: Service History
        self.service_input = QLineEdit(notes or "")
        self.service_input.setPlaceholderText("Service & Repair Log...")
        self.service_input.setProperty("class", "prof_clean_input")
        self.service_input.textChanged.connect(self.data_changed.emit)
        l_service = QLabel("Service:"); l_service.setStyleSheet(lbl_style)
        grid.addWidget(l_service, 3, 0)
        grid.addWidget(self.service_input, 3, 1, 1, 3)
        
        self.form_layout.addLayout(grid)
        
        self.btn_measure = QPushButton("Select IEM")
        self.btn_measure.setToolTip("Select this IEM for measurement")
        self.btn_measure.setCursor(Qt.PointingHandCursor)
        self.btn_measure.setStyleSheet('''
            QPushButton { background-color: #10b981; color: black; border-radius: 4px; padding: 6px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #059669; }
        ''')
        self.btn_measure.clicked.connect(lambda: self.load_requested.emit(self.iem_id))
        self.form_layout.addWidget(self.btn_measure)
        
        self.form_layout.addStretch()
        self.main_layout.addWidget(self.form_container)
        
        self.form_container.setFixedWidth(0)
        self.form_container.hide()
        self.setProperty("class", "iem_card_wrapper")
        
        self._form_width = 0
        self.anim = QPropertyAnimation(self, b"formWidth")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    @Property(int)
    def formWidth(self):
        return self._form_width
        
    @formWidth.setter
    def formWidth(self, w):
        self._form_width = w
        self.form_container.setFixedWidth(w)

    def set_avatar_size(self, size):
        self.pic_widget.set_size(size)
        # Sizing is handled by CSS now
        
    def handle_pic_click(self):
        if not self.expanded:
            self.toggle_expand()
        else:
            self.choose_pic()
            
    def enterEvent(self, event):
        if not self.expanded:
            self.set_title_active(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        if not self.expanded:
            self.set_title_active(False)
        super().leaveEvent(event)
        
    def set_title_active(self, active):
        pass # Styling handled by CSS classes
            
    def sync_title(self, *args):
        cname = self.custom_name_input.text().strip()
        mname = self.model_input.currentText().strip()
        val = f"{cname}\n[{mname}]" if cname else (mname or "Unknown IEM")
        self.lbl_title.setText(val)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_expand()
            
    def toggle_expand(self):
        self.expanded = not self.expanded
        self.anim.stop()
        
        if self.expanded:
            self.form_container.show()
            self.anim.setStartValue(self.form_container.width())
            self.anim.setEndValue(480)
            self.set_title_active(True)
            pass
            self.pic_widget.overlay.setText("Change")
        else:
            self.anim.setStartValue(self.form_container.width())
            self.anim.setEndValue(0)
            self.anim.finished.connect(self.hide_form_after_anim)
            self.set_title_active(False)
            pass
            self.pic_widget.overlay.setText("Expand")
            
        self.anim.start()
        self.expanded_state_changed.emit()

    def hide_form_after_anim(self):
        if not self.expanded:
            self.form_container.hide()

    def choose_color(self):
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        dlg = QColorDialog(QColor(self.iem_color), self)
        if dlg.exec():
            color = dlg.currentColor().name()
            self.iem_color = color
            self.apply_color()
            self.data_changed.emit()
            
    def apply_color(self):
        if not self.pic_path:
            self.btn_pick_color.show()
            self.btn_remove_pic.hide()
            # Contrast text color calculation
            hex_color = self.iem_color.lstrip('#')
            if len(hex_color) == 6:
                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                text_color = "#000000" if luminance > 0.5 else "#ffffff"
            else:
                text_color = "#ffffff"
                
            self.pic_widget.img_label.setStyleSheet(f"background-color: {self.iem_color}; border-radius: {self.pic_widget.size_val//2}px; border: 1px solid #555; color: {text_color}; font-size: {max(9, int(self.pic_widget.size_val * 0.12))}px; font-weight: bold;")
        else:
            self.btn_pick_color.hide()
            self.btn_remove_pic.show()

    def remove_pic(self):
        self.pic_path = ""
        self.pic_widget.set_image("")
        self.apply_color()
        self.data_changed.emit()

    def choose_pic(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select IEM Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.pic_path = file_path
            self.pic_widget.set_image(self.pic_path)
            self.apply_color() # Re-evaluate
            self.data_changed.emit()
            
    def get_data(self):
        return {
            "id": self.iem_id,
            "model_name": self.model_input.currentText(),
            "contact_person": self.contact_input.text(),
            "service_notes": self.service_input.text(),
            "iem_pic": self.pic_path,
            "abbr": self.abbr_input.text().upper(),
            "custom_name": self.custom_name_input.text(),
            "color": self.iem_color
        }



class AddIEMCardWidget(QFrame):
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "iem-card")
        self.setFixedSize(140, 260)
        self.setStyleSheet("QFrame.iem-card { background-color: transparent; border: 2px dashed #34d399; border-radius: 12px; } QFrame.iem-card:hover { background-color: rgba(52, 211, 153, 0.1); }")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_plus = QLabel("+")
        self.lbl_plus.setAlignment(Qt.AlignCenter)
        self.lbl_plus.setStyleSheet("font-size: 36px; color: #34d399; border: none; font-weight: bold; background: transparent;")
        
        self.lbl_text = QLabel("Add IEM Pair")
        self.lbl_text.setAlignment(Qt.AlignCenter)
        self.lbl_text.setStyleSheet("font-size: 13px; color: #34d399; font-weight: bold; border: none; background: transparent;")
        
        self.main_layout.addWidget(self.lbl_plus)
        self.main_layout.addWidget(self.lbl_text)
        
        self.setCursor(Qt.PointingHandCursor)
        # Set a fixed width, let height be flexible or set a minimum height
        self.setFixedWidth(120)
        self.setMinimumHeight(150)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class ProfileWidget(QWidget):
    profile_updated = Signal()
    profile_data_saved = Signal()
    load_measurement_requested = Signal(int)
    profile_deleted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_musician_id = None
        self.pic_path = ""
        self.iem_cards = []
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #18181b; color: white; font-size: 13px; }
            QLabel.card-title { font-size: 18px; font-weight: bold; color: #00FFFF; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Empty State
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_all)
        
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_lbl = QLabel("Select a musician from the left sidebar to view their profile.\n\nOr click the '+' button to create a new one.")
        empty_lbl.setAlignment(Qt.AlignCenter)
        empty_lbl.setWordWrap(True)
        empty_lbl.setStyleSheet("color: #666; font-size: 16px;")
        empty_layout.addWidget(empty_lbl)
        main_layout.addWidget(self.empty_widget)

        # Content State
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # ==========================================
        # TOP HEADER: Musician Profile (2026 Sleek)
        # ==========================================
        header_layout = QHBoxLayout()
        header_layout.setSpacing(30)

        # Avatar
        pic_layout = QVBoxLayout()
        pic_layout.setAlignment(Qt.AlignCenter)
        
        self.pic_widget = ProfilePicWidget(size=160, placeholder="Add Photo")
        self.pic_widget.clicked.connect(self.choose_pic)
        pic_layout.addWidget(self.pic_widget)
        
        self.btn_remove_profile_pic = QPushButton("Remove Photo")
        self.btn_remove_profile_pic.setStyleSheet("QPushButton { background-color: #500; color: white; border-radius: 4px; padding: 4px 8px; font-size: 10px; margin-top: 5px; } QPushButton:hover { background-color: #700; }")
        self.btn_remove_profile_pic.setCursor(Qt.PointingHandCursor)
        self.btn_remove_profile_pic.clicked.connect(self.remove_pic)
        pic_layout.addWidget(self.btn_remove_profile_pic, alignment=Qt.AlignCenter)
        
        header_layout.addLayout(pic_layout)
        
        # Data Block
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignVCenter)
        
        title_row = QHBoxLayout()
        lbl_musician_title = QLabel("Musician Profile")
        lbl_musician_title.setProperty("class", "card-title")
        title_row.addWidget(lbl_musician_title)
        title_row.addStretch()
        
        self.lbl_saved = QLabel("Saved")
        self.lbl_saved.setStyleSheet("color: #10b981; font-weight: bold; font-size: 13px; background: transparent; border: none;")
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        self.save_opacity = QGraphicsOpacityEffect(self.lbl_saved)
        self.save_opacity.setOpacity(0.0)
        self.lbl_saved.setGraphicsEffect(self.save_opacity)
        title_row.addWidget(self.lbl_saved)
        title_row.addSpacing(15)
        
        self.btn_delete_musician = QPushButton("Delete")
        self.btn_delete_musician.setToolTip("Delete this musician profile")
        self.btn_delete_musician.setCursor(Qt.PointingHandCursor)
        self.btn_delete_musician.setStyleSheet("background-color: transparent; color: #f87171; border: 1px solid #f87171; padding: 4px 12px; border-radius: 12px; font-size: 11px;")
        self.btn_delete_musician.clicked.connect(self.delete_musician)
        
        title_row.addWidget(self.btn_delete_musician)
        info_layout.addLayout(title_row)
        info_layout.addSpacing(10)

        # Sleek Inputs
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        lbl_name = QLabel("Name:", styleSheet="color: #888; font-size: 12px;")
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("background-color: transparent; border: none; border-bottom: 1px solid #444; color: white;")
        row1.addWidget(lbl_name)
        row1.addWidget(self.name_input, stretch=1)
        
        lbl_band = QLabel("Band/Role:", styleSheet="color: #888; font-size: 12px;")
        self.band_input = QLineEdit()
        self.band_input.setStyleSheet("background-color: transparent; border: none; border-bottom: 1px solid #444; color: white;")
        row1.addWidget(lbl_band)
        row1.addWidget(self.band_input, stretch=1)
        self.name_input.textChanged.connect(self.trigger_save)
        self.band_input.textChanged.connect(self.trigger_save)
        info_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        lbl_notes = QLabel("Notes:", styleSheet="color: #888; font-size: 12px;")
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("General notes... (keep it brief)")
        self.notes_input.setStyleSheet("background-color: transparent; border: none; border-bottom: 1px solid #444; color: white;")
        row2.addWidget(lbl_notes)
        row2.addWidget(self.notes_input, stretch=1)
        self.notes_input.textChanged.connect(self.trigger_save)
        info_layout.addLayout(row2)
        
        header_layout.addLayout(info_layout, stretch=1)
        content_layout.addLayout(header_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("border-top: 1px solid #222;")
        content_layout.addWidget(line)

        # ==========================================
        # BOTTOM: IEM Arsenal (Horizontal Flow)
        # ==========================================
        arsenal_header = QHBoxLayout()
        arsenal_title = QLabel("IEM Arsenal")
        arsenal_title.setProperty("class", "card-title")
        arsenal_header.addWidget(arsenal_title)
        arsenal_header.addStretch()
        
        self.btn_add_iem = QPushButton("+ Add IEM")
        self.btn_add_iem.setToolTip("Add a new IEM to this musician")
        self.btn_add_iem.setCursor(Qt.PointingHandCursor)
        self.btn_add_iem.setStyleSheet('''
            QPushButton { background-color: transparent; border: 1px solid #10b981; color: #10b981; border-radius: 4px; padding: 4px 12px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: rgba(16, 185, 129, 0.1); }
        ''')
        self.btn_add_iem.clicked.connect(self.add_another_iem)
        arsenal_header.addWidget(self.btn_add_iem)
        
        content_layout.addLayout(arsenal_header)

        self.iem_scroll = QScrollArea()
        self.iem_scroll.setWidgetResizable(True)
        self.iem_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.iem_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.iem_container = QWidget()
        self.iem_layout = FlowLayout(self.iem_container, margin=0, hSpacing=20, vSpacing=20)
        self.iem_layout.setContentsMargins(0, 0, 0, 0)
        self.iem_layout.setSpacing(20)
        
        self.iem_scroll.setWidget(self.iem_container)
        content_layout.addWidget(self.iem_scroll, stretch=1)
        
        main_layout.addWidget(self.content_widget)
        self.content_widget.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.recalc_avatar_sizes()
        
    def recalc_avatar_sizes(self):
        sender = self.sender()
        if sender and getattr(sender, 'expanded', False):
            for card in self.iem_cards:
                if card != sender and card.expanded:
                    card.toggle_expand()
        
        # Scroll the expanded card into view slightly after animation starts
        if sender and getattr(sender, 'expanded', False):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.iem_scroll.ensureWidgetVisible(sender, 50, 0))


    def trigger_save(self):
        if self.current_musician_id:
            self.save_timer.start(500)

    def load_profile(self, iem_id, m_id=None):
        conn = sqlite3.connect("inearsnitch.db")
        cursor = conn.cursor()
        
        self.current_musician_id = m_id
        if not self.current_musician_id:
            cursor.execute("SELECT musician_id FROM IEM_Models WHERE id = ?", (iem_id,))
            res = cursor.fetchone()
            if res:
                self.current_musician_id = res[0]
                
        if not self.current_musician_id:
            self.content_widget.hide()
            self.empty_widget.show()
            conn.close()
            return
            
        self.content_widget.show()
        self.empty_widget.hide()
        
        cursor.execute("SELECT name, band, notes, profile_pic FROM Musicians WHERE id = ?", (self.current_musician_id,))
        m_res = cursor.fetchone()
        if m_res:
            self.name_input.setText(m_res[0] or "")
            self.band_input.setText(m_res[1] or "")
            self.notes_input.setText(m_res[2] or "")
            self.pic_widget.set_image(m_res[3])
            self.btn_remove_profile_pic.setVisible(bool(m_res[3]))
            
        # Clear old cards
        for i in reversed(range(self.iem_layout.count())):
            widget = self.iem_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.iem_cards.clear()
        
        cursor.execute("SELECT id, model_name, contact_person, service_notes, iem_pic, abbreviation, custom_name, color FROM IEM_Models WHERE musician_id = ?", (self.current_musician_id,))
        iems = cursor.fetchall()
        
        for iem in iems:
            color = iem[7] if len(iem) > 7 and iem[7] else "#2a2a2a"
            card = IEMCardWidget(iem[0], iem[1], iem[2], iem[3], iem[4], iem[5], iem[6], color)
            card.delete_requested.connect(self.delete_iem)
            card.expanded_state_changed.connect(self.recalc_avatar_sizes)
            card.data_changed.connect(self.trigger_save)
            card.load_requested.connect(self.load_measurement_requested.emit)
            self.iem_layout.addWidget(card)
            self.iem_cards.append(card)
            
        self.recalc_avatar_sizes()
        conn.close()

    def choose_pic(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Musician Photo", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if file_path:
            self.pic_widget.set_image(file_path)
            self.btn_remove_profile_pic.show()
            self.save_all()

    def remove_pic(self):
        self.pic_widget.set_image("")
        self.btn_remove_profile_pic.hide()
        self.save_all()
            
    def add_another_iem(self):
        if not self.current_musician_id: return
        
        self.save_all() # Flush any pending changes before reloading UI
        
        conn = sqlite3.connect("inearsnitch.db")
        c = conn.cursor()
        c.execute("INSERT INTO IEM_Models (musician_id, model_name, contact_person, service_notes, iem_pic, custom_name) VALUES (?, ?, '', '', '', '')", 
                  (self.current_musician_id, "New IEM Pair"))
        conn.commit()
        conn.close()
        
        self.load_profile(None, self.current_musician_id) # Refresh the IEM cards to show the newly added one
        self.profile_data_saved.emit()
        
        # Trigger Autosave visual feedback
        from PySide6.QtCore import QPropertyAnimation
        self.save_anim = QPropertyAnimation(self.save_opacity, b"opacity")
        self.save_anim.setDuration(2000)
        self.save_anim.setKeyValueAt(0.0, 0.0)
        self.save_anim.setKeyValueAt(0.1, 1.0)
        self.save_anim.setKeyValueAt(0.7, 1.0)
        self.save_anim.setKeyValueAt(1.0, 0.0)
        self.save_anim.start()

    def delete_musician(self):
        if not self.current_musician_id: return
        reply = QMessageBox.question(self, 'Remove Musician Profile', 'Are you sure? This will permanently delete this musician, all their IEMs, and all measurements.\n\nThis cannot be undone.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect("inearsnitch.db")
            c = conn.cursor()
            c.execute("SELECT id FROM IEM_Models WHERE musician_id = ?", (self.current_musician_id,))
            iems = c.fetchall()
            for iem in iems:
                c.execute("DELETE FROM Measurements WHERE iem_id = ?", (iem[0],))
            c.execute("DELETE FROM IEM_Models WHERE musician_id = ?", (self.current_musician_id,))
            c.execute("DELETE FROM Musicians WHERE id = ?", (self.current_musician_id,))
            conn.commit()
            conn.close()
            self.profile_deleted.emit()

    def delete_iem(self, iem_id):
        reply = QMessageBox.question(self, 'Remove IEM', 'Are you sure? This will permanently delete this IEM and all its measurements.\n\nThis cannot be undone.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect("inearsnitch.db")
            c = conn.cursor()
            c.execute("DELETE FROM Measurements WHERE iem_id = ?", (iem_id,))
            c.execute("DELETE FROM IEM_Models WHERE id = ?", (iem_id,))
            conn.commit()
            conn.close()
            self.load_profile(None, self.current_musician_id)
            self.profile_updated.emit()

    def save_all(self):
        if not self.current_musician_id: return
        conn = sqlite3.connect("inearsnitch.db")
        c = conn.cursor()
        
        try:
            c.execute('''
                UPDATE Musicians 
                SET name = ?, band = ?, notes = ?, profile_pic = ? 
                WHERE id = ?
            ''', (self.name_input.text(), self.band_input.text(), 
                  self.notes_input.text(), self.pic_widget.current_pic_path, self.current_musician_id))
                  
            for card in self.iem_cards:
                data = card.get_data()
                c.execute('''
                    UPDATE IEM_Models 
                    SET model_name = ?, contact_person = ?, service_notes = ?, iem_pic = ?, abbreviation = ?, custom_name = ?, color = ?
                    WHERE id = ?
                ''', (data['model_name'], data['contact_person'], data['service_notes'], data['iem_pic'], data.get('abbr', ''), data.get('custom_name', ''), data.get('color', '#2a2a2a'), data['id']))
                  
            conn.commit()
        finally:
            conn.close()
            
        self.profile_data_saved.emit()
        
        # Trigger Autosave visual feedback
        from PySide6.QtCore import QPropertyAnimation
        self.save_anim = QPropertyAnimation(self.save_opacity, b"opacity")
        self.save_anim.setDuration(2000)
        self.save_anim.setKeyValueAt(0.0, 0.0)
        self.save_anim.setKeyValueAt(0.1, 1.0)
        self.save_anim.setKeyValueAt(0.7, 1.0)
        self.save_anim.setKeyValueAt(1.0, 0.0)
        self.save_anim.start()
