import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

# Fix 1: Clear legends properly before plotting
def insert_legend_clear(match):
    prefix = match.group(1)
    widget_name = match.group(2)
    return f"{prefix}{widget_name}.clear()\n        if {widget_name}.plotItem.legend:\n            {widget_name}.plotItem.legend.clear()\n"

code = re.sub(r'([ \t]+)(self\.\w+_widget)\.clear\(\)\n', insert_legend_clear, code)

# Fix 2: Add CSD legend (it was missing entirely in setup_ui!)
if "self.csd_widget.addLegend" not in code:
    code = code.replace("self.csd_widget.setLogMode(x=True, y=False)", "self.csd_widget.setLogMode(x=True, y=False)\n        self.csd_widget.addLegend(offset=(10, 10))")

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Legends patched.")
