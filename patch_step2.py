import sys
import re

with open('main.py', 'r') as f:
    content = f.read()

# 1. Fix Combobox styles
old_style_tgt = 'self.cb_meas_target.setStyleSheet("QComboBox { background: #222; color: #E0E0E0; border: 1px solid #555; padding: 8px; border-radius: 4px; font-size: 13px; font-weight: 500; } QComboBox::drop-down { border: 0px; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")'
new_style_tgt = 'self.cb_meas_target.setStyleSheet("QComboBox { background: #222; color: #E0E0E0; border: 1px solid #555; padding: 8px; border-radius: 4px; font-size: 13px; font-weight: 500; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")'
content = content.replace(old_style_tgt, new_style_tgt)

old_style_hst = 'self.cb_meas_history.setStyleSheet("QComboBox { background: #222; color: #E0E0E0; border: 1px solid #555; padding: 8px; border-radius: 4px; font-size: 13px; font-weight: 500; } QComboBox::drop-down { border: 0px; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")'
new_style_hst = 'self.cb_meas_history.setStyleSheet("QComboBox { background: #222; color: #E0E0E0; border: 1px solid #555; padding: 8px; border-radius: 4px; font-size: 13px; font-weight: 500; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")'
content = content.replace(old_style_hst, new_style_hst)


# 2. Fix Event filter
old_filter = """                # Make text select all on focus/click so user doesn't have to delete it
                from PyQt5 import QtCore
                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.FocusIn:
                            QtCore.QTimer.singleShot(0, obj.selectAll)
                        elif event.type() == QtCore.QEvent.MouseButtonPress:
                            QtCore.QTimer.singleShot(0, obj.selectAll)
                        return super().eventFilter(obj, event)
                
                # Attach to keep reference
                b._focus_filter = FocusSelectFilter(b)
                line_edit.installEventFilter(b._focus_filter)"""

new_filter = """                # Allow normal click-to-open behavior without eating events
                from PyQt5 import QtCore
                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.FocusIn:
                            QtCore.QTimer.singleShot(0, obj.selectAll)
                        # Remove MouseButtonPress interception so popup opens normally
                        return super().eventFilter(obj, event)
                
                b._focus_filter = FocusSelectFilter(b)
                line_edit.installEventFilter(b._focus_filter)"""
content = content.replace(old_filter, new_filter)

with open('main.py', 'w') as f:
    f.write(content)
