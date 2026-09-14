import re

with open('main.py', 'r') as f:
    content = f.read()

old_code = r"""        except Exception as e:
            self\.error\.emit\(str\(e\)\)"""

new_code = """        except Exception as e:
            import traceback
            traceback.print_exc()  # Prints to stderr, which LogStream catches!
            self.error.emit(str(e))"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    with open('main.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
