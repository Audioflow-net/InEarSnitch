import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''        if idx == 0 and self\.current_iem_id and hasattr\(self\.page_prof, 'load_profile'\):
            m_id = None
            if hasattr\(self, 'active_card'\) and self\.active_card:
                m_id = self\.active_card\.m_id
            self\.page_prof\.load_profile\(self\.current_iem_id, m_id\)
        if idx == 3 and self\.current_iem_id and hasattr\(self\.page_hist, 'load_history'\):
            m_id = None
            if hasattr\(self, 'active_card'\) and self\.active_card:
                m_id = self\.active_card\.m_id
            if m_id is not None:
                self\.page_hist\.load_history\(m_id\)'''

replacement = r'''        if idx == 0 and hasattr(self.page_prof, 'load_profile'):
            m_id = None
            if hasattr(self, 'active_card') and self.active_card:
                m_id = self.active_card.m_id
            if m_id is not None:
                self.page_prof.load_profile(self.current_iem_id, m_id)
        if idx == 3 and hasattr(self.page_hist, 'load_history'):
            m_id = None
            if hasattr(self, 'active_card') and self.active_card:
                m_id = self.active_card.m_id
            if m_id is not None:
                self.page_hist.load_history(m_id)'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Switch tab patched.")
