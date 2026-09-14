import sys

with open('main.py', 'r') as f:
    content = f.read()

old_repaint = """            self.plot_widget.update()
            self.plot_widget.repaint()"""
            
new_repaint = """            target_plot.update()
            target_plot.repaint()"""

content = content.replace(old_repaint, new_repaint)

with open('main.py', 'w') as f:
    f.write(content)
