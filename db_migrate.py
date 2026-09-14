import sqlite3
conn = sqlite3.connect("inearsnitch.db")
c = conn.cursor()
try:
    c.execute("ALTER TABLE IEM_Models ADD COLUMN custom_name TEXT DEFAULT ''")
    conn.commit()
    print("Migration successful.")
except Exception as e:
    print("Migration failed:", e)
conn.close()
