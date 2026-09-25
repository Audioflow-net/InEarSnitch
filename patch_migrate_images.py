import re

with open("main.py", "r") as f:
    content = f.read()

old_migration = """    if os.path.exists(old_db) and not os.path.exists(new_db):
        import shutil
        try:
            shutil.copy2(old_db, new_db)
        except Exception:
            pass"""

new_migration = """    if os.path.exists(old_db) and not os.path.exists(new_db):
        import shutil
        try:
            shutil.copy2(old_db, new_db)
        except Exception:
            pass
            
    # Also migrate images directory if it exists
    old_img = os.path.join(home, "Documents", "InEarSnitch", "images")
    new_img = os.path.join(app_dir, "images")
    if os.path.exists(old_img) and not os.path.exists(new_img):
        import shutil
        try:
            shutil.copytree(old_img, new_img)
        except Exception:
            pass"""

content = content.replace(old_migration, new_migration)

with open("main.py", "w") as f:
    f.write(content)
