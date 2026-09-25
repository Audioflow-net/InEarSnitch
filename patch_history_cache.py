import re

with open("history_ui.py", "r") as f:
    content = f.read()

old_logic = """    def load_history(self, m_id):
        self.last_m_id = m_id
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self.measurements = []
        self.plot_widget.clear()"""

new_logic = """    def load_history(self, m_id, force_reload=False):
        if getattr(self, 'last_m_id', None) == m_id and not force_reload:
            return
        self.last_m_id = m_id
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self.measurements = []
        self.plot_widget.clear()"""

content = content.replace(old_logic, new_logic)

with open("history_ui.py", "w") as f:
    f.write(content)
