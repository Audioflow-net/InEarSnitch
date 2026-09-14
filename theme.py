import sqlite3
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
import pyqtgraph as pg

CURRENT_MODE = "dark"

# Define central theme colors
COLORS = {
    "dark": {
        "bg_main": "#18181b",
        "bg_panel": "#1f1f23",
        "bg_hover": "#2a2a2a",
        "text_primary": "white",
        "text_secondary": "#888888",
        "border": "#555555",
        "accent": "#00FFFF",
        "danger": "#dc2626",
        "danger_text": "white",
        "pg_bg": "#18181b",
        "pg_fg": "w",
        "card_bg": "#1f1f23",
                "watermark": "#50FFFFFF",
        "curve_target": "#FFFFFF",
        "curve_left": "#00FFFF",
        "curve_left_rgb": (0, 255, 255),
        "curve_right": "#FF0055",
                "curve_right_rgb": (255, 0, 85),
        "accent_glow": "rgba(0, 255, 255, 0.15)",
        "accent_glow_soft": "rgba(0, 255, 255, 0.02)",
        "accent_edge": "rgba(0, 255, 255, 0.6)",
        "shadow": "rgba(0, 0, 0, 0.6)" 
    },
    "light": {
        "bg_main": "#f4f4f5",
        "bg_panel": "#ffffff",
        "bg_hover": "#e4e4e7",
        "text_primary": "#18181c",
        "text_secondary": "#52525b",
        "border": "#a1a1aa",
        "accent": "#0284c7",
        "danger": "#dc2626",
        "danger_text": "white",
        "pg_bg": "#f4f4f5",
        "pg_fg": "k",
        "card_bg": "#ffffff",
                "watermark": "#50000000",
        "curve_target": "#18181c",
        "curve_left": "#0284c7",
        "curve_left_rgb": (2, 132, 199),
        "curve_right": "#dc2626",
                "curve_right_rgb": (220, 38, 38),
        "accent_glow": "rgba(2, 132, 199, 0.15)",
        "accent_glow_soft": "rgba(2, 132, 199, 0.02)",
        "accent_edge": "rgba(2, 132, 199, 0.6)",
        "shadow": "rgba(0, 0, 0, 0.15)" 
    }
}

def get_color(role):
    return COLORS[CURRENT_MODE].get(role, "red")

def get_global_qss():
    """Generates the global stylesheet based on the current mode."""
    # Base stylesheet using dynamic properties as 'classes'
    qss = f"""
    QMainWindow, QDialog, .QWidget {{
        background-color: {get_color('bg_main')};
        color: {get_color('text_primary')};
    }}
    

    QToolTip {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
        border: 1px solid {get_color('border')};
        padding: 4px;
        border-radius: 4px;
        font-size: 11px;
    }}



    QDialogButtonBox {{
        qproperty-centerButtons: true;
    }}

    QMessageBox {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
    }}
    QMessageBox QLabel {{
        color: {get_color('text_primary')};
        background-color: transparent;
    }}
    QMessageBox QPushButton {{
        background-color: {get_color('bg_hover')};
        color: {get_color('text_primary')};
        border: 1px solid {get_color('border')};
        padding: 5px 15px;
        border-radius: 4px;
    }}
    QMessageBox QPushButton:hover {{
        border: 1px solid {get_color('accent')};
    }}

    QLabel {{
        background-color: transparent !important;
    }}
    
    QLabel[class="title"] {{
        font-weight: bold;
        font-size: 16px;
        color: {get_color('text_primary')};
    }}
    
    QLabel[class="subtitle"] {{
        font-weight: bold;
        font-size: 12px;
        color: {get_color('text_secondary')};
    }}
    
    QPushButton {{
        background-color: {get_color('bg_panel')};
        border: 1px solid {get_color('border')};
        border-radius: 4px;
        padding: 5px;
        color: {get_color('text_primary')};
    }}
    
    QPushButton:hover {{
        background-color: {get_color('bg_hover')};
    }}
    
    QPushButton[class="danger"] {{
        background-color: {get_color('danger')};
        color: {get_color('danger_text')};
        border: none;
        font-weight: bold;
        padding: 8px;
    }}
    
    
    QPushButton[class="danger"]:disabled {{
        background-color: {get_color('bg_hover')};
        color: {get_color('text_secondary')};
    }}

    QPushButton[class="danger"]:hover {{
        background-color: #b91c1c;
    }}
    
    QPushButton[class="accent"] {{
        background-color: {get_color('accent')};
        color: white;
        border: none;
        font-weight: bold;
    }}
    


    QPushButton[class="chan_toggle"] {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_secondary')};
        border: 1px solid {get_color('border')};
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
    }}
    QPushButton[class="chan_toggle"]:hover {{
        background-color: {get_color('bg_hover')};
        color: {get_color('text_primary')};
        border: 1px solid {get_color('text_secondary')};
    }}
    QPushButton[class="chan_toggle"][chan="L"]:checked {{
        border: 2px solid #0ea5e9;
        color: #0ea5e9;
        background-color: transparent;
    }}
    QPushButton[class="chan_toggle"][chan="R"]:checked {{
        border: 2px solid #ef4444;
        color: #ef4444;
        background-color: transparent;
    }}

    QComboBox QAbstractItemView {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
        selection-background-color: {get_color('bg_hover')};
        selection-color: {get_color('text_primary')};
        border: 1px solid {get_color('border')};
        outline: none;
    }}

    QListWidget, QScrollArea, QComboBox {{
        background-color: {get_color('bg_panel')};
        border: 1px solid {get_color('border')};
        color: {get_color('text_primary')};
    }}
    
    /* History UI Styles */
    QTableWidget {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
        gridline-color: {get_color('border')};
        border: 1px solid {get_color('border')};
    }}
    QHeaderView::section {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_primary')};
        padding: 4px;
        border: 1px solid {get_color('border')};
        font-weight: bold;
    }}
    QTableWidget::item:selected {{
        background-color: {get_color('accent')};
        color: white;
    }}
    QLabel#PhotoLabel {{
        border: 1px solid {get_color('border')}; 
        background-color: {get_color('bg_panel')};
        border-radius: 6px;
    }}

    /* Segmented Buttons */
    QPushButton[class="seg_btn"] {{
        background-color: {get_color('bg_panel')};
        color: {get_color('text_secondary')};
        border: 1px solid {get_color('border')};
        padding: 8px 12px;
        font-weight: bold;
        font-size: 13px;
    }}
    QPushButton[class="seg_btn"]:hover:!checked {{
        background-color: {get_color('bg_hover')};
    }}
    QPushButton[class="seg_btn"][seg_pos="left"] {{
        border-top-right-radius: 0px;
        border-bottom-right-radius: 0px;
        border-right: 0px;
    }}
    QPushButton[class="seg_btn"][seg_pos="middle"] {{
        border-radius: 0px;
        border-right: 0px;
    }}
    QPushButton[class="seg_btn"][seg_pos="right"] {{
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
    }}
    QPushButton[class="seg_btn"]:checked {{
        border-color: {get_color('border')};
        color: white;
    }}
    QPushButton[class="seg_btn"][checked_bg="green"]:checked {{
        background-color: #16a34a;
    }}
    QPushButton[class="seg_btn"][checked_bg="red"]:checked {{
        background-color: #dc2626;
    }}
    QPushButton[class="seg_btn"][checked_bg="default"]:checked {{
        background-color: {get_color('bg_hover')};
        color: {get_color('text_primary')};
    }}

    QWidget[class="musician_card"] {{
        background-color: #2d2d34;
        border-radius: 8px;
        border: none;
    }}
    QWidget[class="musician_card"]:hover {{
        background-color: #3f3f46;
        border-radius: 8px;
    }}
    QWidget[class="musician_card"][selected="true"] {{
        background-color: #3f3f46;
        border-radius: 8px;
        border: 2px solid {get_color('accent')};
    }}    QLabel[class="avatar_btn"] {{
        background-color: #1f1f23;
        border: 2px solid #2d2d34;
        border-radius: 18px;
        color: {get_color('text_secondary')};
        font-size: 14px;
        font-weight: bold;
    }}
    QLabel[class="avatar_btn"]:hover {{
        background-color: #3f3f46;
        border: 2px solid #3f3f46;
        color: {get_color('text_primary')};
    }}
    QLabel[class="avatar_btn"][selected="true"] {{
        background-color: {get_color('accent')};
        color: #000000;
        border: 2px solid {get_color('accent')};
    }}
    
    QLabel[class="avatar_btn_pic"] {{
        background-color: transparent;
        border: 2px solid {get_color('border')};
        border-radius: 18px;
        color: {get_color('text_secondary')};
        font-size: 14px;
        font-weight: bold;
    }}
    QLabel[class="avatar_btn_pic"]:hover {{
        background-color: transparent;
        border: 2px solid {get_color('text_secondary')};
    }}
    QLabel[class="avatar_btn_pic"][selected="true"] {{
        background-color: transparent;
        border: 2px solid {get_color('accent')};
    }}


    
    QFrame[class="iem_card_wrapper"] {{
        background-color: transparent;
    }}
    QFrame[class="iem_avatar_panel"] {{
        background-color: {get_color('bg_panel')};
        border-radius: 20px;
        border: 1px solid {get_color('border')};
    }}
    QLabel[class="iem_avatar_title"] {{
        font-weight: bold;
        font-size: 16px;
        color: {get_color('text_primary')};
        margin-top: 5px;
    }}
    QFrame[class="iem_form_panel"] {{
        background-color: {get_color('bg_main')};
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
        border: 1px solid {get_color('border')};
        border-left: none;
    }}
    QComboBox[class="iem_clean_title"] {{
        background: transparent;
        border: none;
        font-size: 20px;
        font-weight: bold;
        color: {get_color('text_primary')};
    }}
    QComboBox[class="iem_clean_title"]::drop-down {{
        border: none;
        width: 20px;
    }}
    QLineEdit[class="iem_clean_input"] {{
        background: transparent;
        border: none;
        border-bottom: 1px solid {get_color('border')};
        color: {get_color('text_secondary')};
        font-size: 14px;
        padding-bottom: 2px;
    }}
    QLineEdit[class="iem_clean_input"]:focus {{
        border-bottom: 1px solid {get_color('accent')};
        color: {get_color('text_primary')};
    }}
    QLineEdit[class="iem_clean_abbr"] {{
        background: transparent;
        border: none;
        border-bottom: 2px solid {get_color('accent')};
        color: {get_color('accent')};
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        padding-bottom: 2px;
    }}
    QPushButton[class="iem_btn_delete"] {{
        background: transparent;
        color: #ef4444;
        font-size: 18px;
        font-weight: bold;
        border: none;
        padding: 5px;
    }}
    QPushButton[class="iem_btn_delete"]:hover {{
        background: #fef2f2;
        border-radius: 15px;
    }}

    QWidget[class="panel"] {{
        background-color: {get_color('bg_panel')};
        border-radius: 4px;
        border: 1px solid {get_color('border')};
    }}
    
    QLabel[class="watermark"] {{
        color: {get_color('watermark')} !important;
        font-size: 32px !important;
        font-weight: bold !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }}
    """
    return qss

# Keep the original method for legacy monkey patching temporarily
_original_set_style = QWidget.setStyleSheet

def patched_set_style(self, qss):
    """Legacy monkey patch to handle hardcoded styles not yet migrated to the new class system."""
    self._original_qss = qss
    if CURRENT_MODE == "light":
        replacements = [
            ("background-color: transparent !important; color: white;", "background-color: transparent !important; color: #18181b;"),
            ("background-color: #004444", "background-color: #e0f2fe"),
            ("background-color: #7f1d1d", "background-color: #fef2f2; border: 1px solid #f87171"),
            ("color: red", "color: #dc2626"),
            ("#18181b", "#f4f4f5"),
            ("#111", "#ffffff"),
            ("#202022", "#d4d4d8"),
            ("#1f1f23", "#ffffff"),
            ("#222225", "#ffffff"),
            ("#27272a", "#ffffff"),
            ("#1a1a1a", "#e4e4e7"),
            ("#2a2a2a", "#d4d4d8"),
            ("#2d2d34", "#ffffff"),
            ("#222", "#ffffff"),
            ("#333", "#d4d4d8"),
            ("#3f3f46", "#e4e4e7"),
            ("#444", "#d4d4d8"),
            ("#555", "#a1a1aa"),
            ("#666", "#71717a"),
            ("#888", "#52525b"),
            ("#aaa", "#52525b"),
            ("#AAA", "#52525b"),
            ("#ccc", "#52525b"),
            ("#ddd", "#3f3f46"),
            ("#00FFFF", "#0284c7"),
            ("#00FF99", "#059669"),
            ("#FFBB00", "#d97706"),
            ("#34d399", "#059669"),
            ("#f87171", "#dc2626")
        ]
        # Only replace "white" if it's likely a text color or explicitly requested, 
        # to avoid ruining our newly classed buttons that explicitly want white text on dark backgrounds.
        if "color: white" in qss:
            qss = qss.replace("color: white", "color: __TEXT_PRIMARY__")
            
        for dark, light in replacements:
            qss = qss.replace(dark, light)
            
        qss = qss.replace("__TEXT_PRIMARY__", "#18181b")
            
    _original_set_style(self, qss)

def init_theme(db_path="inearsnitch.db"):
    global CURRENT_MODE
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS AppSettings (key TEXT PRIMARY KEY, value TEXT)")
        c.execute("SELECT value FROM AppSettings WHERE key = 'theme'")
        res = c.fetchone()
        if res:
            CURRENT_MODE = res[0]
        else:
            c.execute("INSERT INTO AppSettings (key, value) VALUES ('theme', 'dark')")
            conn.commit()
        conn.close()
    except Exception as e:
        print("Theme DB error:", e)

    QWidget.setStyleSheet = patched_set_style
    
    # Configure pyqtgraph globals
    pg.setConfigOption('background', get_color('pg_bg'))
    pg.setConfigOption('foreground', get_color('pg_fg'))

    # Apply global stylesheet if a QApplication instance exists
    app = QApplication.instance()
    if app:
        app.setStyleSheet(get_global_qss())

def toggle_theme(parent, db_path="inearsnitch.db"):
    global CURRENT_MODE
    CURRENT_MODE = "light" if CURRENT_MODE == "dark" else "dark"
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE AppSettings SET value = ? WHERE key = 'theme'", (CURRENT_MODE,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error saving theme:", e)
        
    pg.setConfigOption('background', get_color('pg_bg'))
    pg.setConfigOption('foreground', get_color('pg_fg'))
    
    app = QApplication.instance()
    if app:
        app.setStyleSheet(get_global_qss())
        
    def reapply(widget):
        # Repolish global style
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        
        # Reapply legacy inline styles
        if hasattr(widget, '_original_qss'):
            widget.setStyleSheet(widget._original_qss)
        for child in widget.children():
            if isinstance(child, QWidget):
                reapply(child)
                
    for tlw in QApplication.topLevelWidgets():
        reapply(tlw)
        for plot in tlw.findChildren(pg.PlotWidget):
            plot.setBackground(get_color('pg_bg'))
            fg = get_color('pg_fg')
            ax_l = plot.getAxis('left')
            ax_b = plot.getAxis('bottom')
            if ax_l:
                ax_l.setPen(fg)
                ax_l.setTextPen(fg)
            if ax_b:
                ax_b.setPen(fg)
                ax_b.setTextPen(fg)
            
            # Fix pyqtgraph Titles (which don't read from QSS)
            # We must re-set the title color dynamically!
            if hasattr(plot, 'titleLabel') and plot.titleLabel.text:
                current_text = plot.titleLabel.text
                plot.setTitle(current_text, color=fg, size="14pt")

def is_light():
    return CURRENT_MODE == "light"
