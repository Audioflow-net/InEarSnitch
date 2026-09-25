import re

with open("InEarSnitch.spec", "r") as f:
    content = f.read()

old_datas = """datas = [
    # Handbücher
    (os.path.join(PROJECT_DIR, 'manual_de.md'), '.'),
    (os.path.join(PROJECT_DIR, 'manual_en.md'), '.'),
    (os.path.join(PROJECT_DIR, 'manual_es.md'), '.'),
    # Reference Targets (kompletter Ordner)
    (os.path.join(PROJECT_DIR, 'reference_targets'), 'reference_targets'),
    # Werksmäßige Mikrofonkalibrierungen
    (os.path.join(PROJECT_DIR, 'calibrations'), 'calibrations'),
]"""

new_datas = """datas = [
    # Handbücher
    (os.path.join(PROJECT_DIR, 'manual_de.md'), '.'),
    (os.path.join(PROJECT_DIR, 'manual_en.md'), '.'),
    (os.path.join(PROJECT_DIR, 'manual_es.md'), '.'),
    # Reference Targets (kompletter Ordner)
    (os.path.join(PROJECT_DIR, 'reference_targets'), 'reference_targets'),
    # Werksmäßige Mikrofonkalibrierungen
    (os.path.join(PROJECT_DIR, 'calibrations'), 'calibrations'),
    # Assets (Tips 3D Renders)
    (os.path.join(PROJECT_DIR, 'assets'), 'assets'),
    # App Logo
    (os.path.join(PROJECT_DIR, 'Final Logo InEar Snitch.png'), '.'),
]"""

content = content.replace(old_datas, new_datas)

with open("InEarSnitch.spec", "w") as f:
    f.write(content)
