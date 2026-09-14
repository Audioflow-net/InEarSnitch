import os
import sys

def get_data_dir():
    """Get a safe, writable directory for application data."""
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, "Documents", "InEarSnitch")
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir)
        except Exception:
            pass
    return app_dir

def get_db_path():
    """Get the absolute path to the SQLite database."""
    # If running from source (not frozen), we can just use the local directory
    # but to be safe and consistent, we'll use Documents/InEar Snitch/inearsnitch.db for frozen apps
    if getattr(sys, 'frozen', False):
        return os.path.join(get_data_dir(), "inearsnitch.db")
    else:
        # Development mode: use local db
        return "inearsnitch.db"
