import re

with open('profile_ui.py', 'r') as f:
    content = f.read()

optimized_func = """def create_circular_pixmap(image_reader, size):
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
"""

content = re.sub(
    r'def create_circular_pixmap\(image_reader, size\):.*?(?=\nclass ProfilePicWidget|\n\n)',
    optimized_func,
    content,
    flags=re.DOTALL
)

with open('profile_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
