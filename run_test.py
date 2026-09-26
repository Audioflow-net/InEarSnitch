import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from test_searchable import SearchableComboBox

def test():
    app = QApplication(sys.argv)
    cb = SearchableComboBox()
    cb.addItems(["Apple", "Banana", "Cherry"])
    cb.show()
    
    cb.setCurrentIndex(1) # Banana
    print("Initial:", cb.currentText())
    
    # Simulate focus and mouse click
    cb.lineEdit().setFocus()
    QTest.mouseClick(cb.lineEdit(), Qt.LeftButton)
    
    print("After click:", cb.lineEdit().text(), "Selected:", cb.lineEdit().selectedText())
    
    # Simulate type 'X'
    QTest.keyClicks(cb.lineEdit(), "X")
    print("After typing X:", cb.lineEdit().text())
    
    # Simulate Esc
    QTest.keyClick(cb.lineEdit(), Qt.Key_Escape)
    print("After Esc:", cb.lineEdit().text())
    
    # Simulate lose focus
    cb.lineEdit().clearFocus()
    
    print("After focus lost:", cb.lineEdit().text())
    
    app.quit()

if __name__ == "__main__":
    test()
