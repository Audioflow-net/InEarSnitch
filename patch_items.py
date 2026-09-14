import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_items = """        for p in [self.plot_widget, self.thd_widget]:
            items_to_remove = [item for item in p.items if isinstance(item, pg.LinearRegionItem)]
            for item in items_to_remove:
                p.removeItem(item)"""

new_items = """        for p in [self.plot_widget, self.thd_widget]:
            try:
                items_to_remove = [item for item in p.plotItem.items if isinstance(item, pg.LinearRegionItem)]
                for item in items_to_remove:
                    p.removeItem(item)
            except Exception:
                pass"""
content = content.replace(old_items, new_items)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
