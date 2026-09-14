import sys
import os
import traceback

def audit():
    errors = []
    
    print("1. Checking syntax and imports...")
    modules = ["main", "audio_engine", "analysis", "analysis_ui", "history_ui", "profile_ui", "database", "theme"]
    for mod in modules:
        try:
            __import__(mod)
        except Exception as e:
            errors.append(f"Import error in {mod}.py: {e}\n{traceback.format_exc()}")
            
    print("2. Checking DB schema...")
    import sqlite3
    try:
        conn = sqlite3.connect("inearsnitch.db")
        c = conn.cursor()
        c.execute("PRAGMA integrity_check")
        res = c.fetchone()
        if res[0] != "ok":
            errors.append(f"DB integrity check failed: {res}")
            
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in c.fetchall()]
        print(f"Tables found: {tables}")
        conn.close()
    except Exception as e:
        errors.append(f"DB error: {e}")
        
    if errors:
        print("\nERRORS FOUND:")
        for err in errors:
            print(err)
    else:
        print("\nAll automated checks passed!")

if __name__ == "__main__":
    audit()
