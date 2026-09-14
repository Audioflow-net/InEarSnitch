import sys

with open('main.py', 'r') as f:
    content = f.read()

# Add auto-switch to Analysis tab when live RTA starts
old_code = """            self.live_rta_line = self.plot_widget.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")
            self.live_rta_line.show()"""

new_code = """            self.live_rta_line = self.plot_widget.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")
            self.live_rta_line.show()
            self.switch_workspace_tab(2)"""

content = content.replace(old_code, new_code)

with open('main.py', 'w') as f:
    f.write(content)
