from PyQt5.QtCore import QSettings, QCoreApplication
import sys
app = QCoreApplication(sys.argv)
settings = QSettings("InEar Snitch", "App")
print("Input:", settings.value("input_device"))
print("Output:", settings.value("output_device"))
