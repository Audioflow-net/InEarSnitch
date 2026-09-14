import re

with open("history_ui.py", "r") as f:
    code = f.read()

code = code.replace(
    'SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name',
    'SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name'
)

code = code.replace(
    'timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob, iem_name = row',
    'timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob, iem_name, custom_name = row\n                display_name = custom_name if custom_name else iem_name'
)

code = code.replace(
    'iem_item = QTableWidgetItem(iem_name)',
    'iem_item = QTableWidgetItem(display_name)'
)

with open("history_ui.py", "w") as f:
    f.write(code)

print("History UI patched.")
