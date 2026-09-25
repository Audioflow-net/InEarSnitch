import re

with open("profile_ui.py", "r") as f:
    content = f.read()

old_logic = """    def load_profile(self, iem_id, m_id=None):
        conn = sqlite3.connect("inearsnitch.db")
        cursor = conn.cursor()
        
        self.current_musician_id = m_id
        if not self.current_musician_id:
            cursor.execute("SELECT musician_id FROM IEM_Models WHERE id = ?", (iem_id,))
            res = cursor.fetchone()
            if res:
                self.current_musician_id = res[0]
                
        if not self.current_musician_id:"""

new_logic = """    def load_profile(self, iem_id, m_id=None, force_reload=False):
        conn = sqlite3.connect("inearsnitch.db")
        cursor = conn.cursor()
        
        target_m_id = m_id
        if not target_m_id:
            cursor.execute("SELECT musician_id FROM IEM_Models WHERE id = ?", (iem_id,))
            res = cursor.fetchone()
            if res:
                target_m_id = res[0]
                
        if target_m_id == self.current_musician_id and not force_reload:
            conn.close()
            return
            
        self.current_musician_id = target_m_id
        
        if not self.current_musician_id:"""

content = content.replace(old_logic, new_logic)

with open("profile_ui.py", "w") as f:
    f.write(content)
