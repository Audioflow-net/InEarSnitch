import re

with open("history_ui.py", "r") as f:
    code = f.read()

old_code = """            conn.commit()
            conn.close()
            
            self.load_history(iem_id)"""

new_code = """            c.execute("SELECT musician_id FROM IEM_Models WHERE id = ?", (iem_id,))
            res = c.fetchone()
            m_id = res[0] if res else None
            conn.commit()
            conn.close()
            
            if m_id is not None:
                self.load_history(m_id)"""

code = code.replace(old_code, new_code)

with open("history_ui.py", "w") as f:
    f.write(code)
