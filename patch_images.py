import re

with open("profile_ui.py", "r") as f:
    content = f.read()

# Add import uuid and shutil at the top if not present
if "import uuid" not in content:
    content = "import uuid\nimport shutil\n" + content

# 1. Musician Profile choose_pic
musician_choose_old = """    def choose_pic(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Musician Photo", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if file_path:
            self.pic_widget.set_image(file_path)
            self.save_all()"""

musician_choose_new = """    def _copy_to_local_images(self, source_path):
        if not source_path or not os.path.exists(source_path): return ""
        img_dir = os.path.join(os.getcwd(), "images")
        os.makedirs(img_dir, exist_ok=True)
        ext = os.path.splitext(source_path)[1]
        new_filename = str(uuid.uuid4()) + ext
        dest_path = os.path.join(img_dir, new_filename)
        try:
            shutil.copy2(source_path, dest_path)
            return os.path.join("images", new_filename)
        except Exception as e:
            print("Failed to copy image:", e)
            return source_path

    def choose_pic(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Musician Photo", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if file_path:
            local_path = self._copy_to_local_images(file_path)
            self.pic_widget.set_image(local_path)
            self.save_all()"""

content = content.replace(musician_choose_old, musician_choose_new)

# 2. IEM Card choose_pic
iem_choose_old = """    def choose_pic(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select IEM Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.pic_path = file_path
            self.pic_widget.set_image(self.pic_path)
            self.apply_color() # Re-evaluate
            self.data_changed.emit()"""

iem_choose_new = """    def _copy_to_local_images(self, source_path):
        if not source_path or not os.path.exists(source_path): return ""
        import os, uuid, shutil
        img_dir = os.path.join(os.getcwd(), "images")
        os.makedirs(img_dir, exist_ok=True)
        ext = os.path.splitext(source_path)[1]
        new_filename = str(uuid.uuid4()) + ext
        dest_path = os.path.join(img_dir, new_filename)
        try:
            shutil.copy2(source_path, dest_path)
            return os.path.join("images", new_filename)
        except Exception:
            return source_path

    def choose_pic(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select IEM Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.pic_path = self._copy_to_local_images(file_path)
            self.pic_widget.set_image(self.pic_path)
            self.apply_color() # Re-evaluate
            self.data_changed.emit()"""

content = content.replace(iem_choose_old, iem_choose_new)

with open("profile_ui.py", "w") as f:
    f.write(content)
