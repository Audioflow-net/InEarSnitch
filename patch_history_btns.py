import re

with open("history_ui.py", "r") as f:
    content = f.read()

old_l = """self.btn_chan_l.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: {active}; color: {fg}; border-color: {border}; }}")"""
new_l = """self.btn_chan_l.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: #0ea5e9; color: white; border-color: #0ea5e9; }}")"""

old_r = """self.btn_chan_r.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: {active}; color: {fg}; border-color: {border}; }}")"""
new_r = """self.btn_chan_r.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: #ef4444; color: white; border-color: #ef4444; }}")"""

content = content.replace(old_l, new_l)
content = content.replace(old_r, new_r)

with open("history_ui.py", "w") as f:
    f.write(content)
