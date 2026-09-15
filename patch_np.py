import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

content = content.replace("    def render_diagnostics(self):", "    def render_diagnostics(self):\n        import numpy as np")

with open("analysis_ui.py", "w") as f:
    f.write(content)
