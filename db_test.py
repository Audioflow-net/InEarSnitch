import sqlite3
conn = sqlite3.connect("inearsnitch.db")
c = conn.cursor()
c.execute("SELECT id, name FROM Musicians")
print("Musicians:", c.fetchall())

c.execute("SELECT id, model_name, musician_id FROM IEM_Models")
print("IEMs:", c.fetchall())

c.execute("SELECT id, iem_id, timestamp FROM Measurements")
print("Measurements:", c.fetchall())
