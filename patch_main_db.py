import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'cursor.execute("SELECT id, model_name, iem_pic, abbreviation FROM IEM_Models WHERE musician_id = ?", (m_id,))',
    'cursor.execute("SELECT id, model_name, iem_pic, abbreviation, custom_name FROM IEM_Models WHERE musician_id = ?", (m_id,))'
)

# In MusicianCard, we need to pass custom_name
# iems is currently [(id, model, pic, abbr), ...]
# now it's [(id, model, pic, abbr, cname), ...]
# Let's find where iems = [(-1, "Unknown IEM", "", "")] is
code = code.replace(
    'iems = [(-1, "Unknown IEM", "", "")]',
    'iems = [(-1, "Unknown IEM", "", "", "")]'
)

with open("main.py", "w") as f:
    f.write(code)

print("Main DB query patched.")
