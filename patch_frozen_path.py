import re

with open("main.py", "r") as f:
    content = f.read()

old_frozen = """if getattr(sys, 'frozen', False):
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, "Documents", "InEarSnitch")
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir)
        except Exception:
            pass
    # Set the working directory to the user's documents folder
    # so all relative paths (inearsnitch.db, reference_targets, etc) are saved there.
    os.chdir(app_dir)"""

new_frozen = """if getattr(sys, 'frozen', False):
    home = os.path.expanduser("~")
    
    # Use Library/Application Support to avoid macOS TCC permission prompts
    # which block read/write access to Documents in distributed .app bundles!
    if sys.platform == 'darwin':
        app_dir = os.path.join(home, "Library", "Application Support", "InEarSnitch")
    elif sys.platform == 'win32':
        app_dir = os.path.join(os.environ.get('APPDATA', home), "InEarSnitch")
    else:
        app_dir = os.path.join(home, ".config", "InEarSnitch")
        
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir)
        except Exception as e:
            print("Failed to create app_dir:", e)
            
    # Copy existing DB from Documents if it exists (Migration)
    old_db = os.path.join(home, "Documents", "InEarSnitch", "inearsnitch.db")
    new_db = os.path.join(app_dir, "inearsnitch.db")
    if os.path.exists(old_db) and not os.path.exists(new_db):
        import shutil
        try:
            shutil.copy2(old_db, new_db)
        except Exception:
            pass
            
    try:
        os.chdir(app_dir)
    except Exception as e:
        print("Failed to chdir:", e)"""

content = content.replace(old_frozen, new_frozen)

with open("main.py", "w") as f:
    f.write(content)
