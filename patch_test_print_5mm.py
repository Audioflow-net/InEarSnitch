from PySide6.QtGui import QImageReader, QImage, QColor, QPainter, QPixmap
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

def create_circular_pixmap(image_reader, size):
    image_reader.setAutoTransform(True)
    orig_size = image_reader.size()
    if not orig_size.isEmpty():
        min_dim = min(orig_size.width(), orig_size.height())
        if min_dim > size * 2: 
            scale_factor = (size * 2) / min_dim
            new_w = int(orig_size.width() * scale_factor)
            new_h = int(orig_size.height() * scale_factor)
            image_reader.setScaledSize(QSize(new_w, new_h))
            
    img = image_reader.read()
    if img.isNull():
        return None
        
    w = img.width()
    h = img.height()
    
    min_dim = min(w, h)
    x_offset = (w - min_dim) // 2
    y_offset = (h - min_dim) // 2
        
    square_img = img.copy(x_offset, y_offset, min_dim, min_dim)
    scaled_img = square_img.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # 3. Create a transparent QImage (guaranteed alpha channel) and draw a circle
    target = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    target.fill(Qt.transparent)
    
    painter = QPainter(target)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    from PySide6.QtGui import QPainterPath
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    
    painter.drawImage(0, 0, scaled_img)
    painter.end()
    
    return QPixmap.fromImage(target)

# Create a dummy solid red image
dummy = QImage(100, 100, QImage.Format_RGB32)
dummy.fill(QColor("red"))
dummy.save("dummy_red.png")

reader = QImageReader("dummy_red.png")
pix = create_circular_pixmap(reader, 100)
pix.save("test_out.png")
print("Saved test_out.png")
