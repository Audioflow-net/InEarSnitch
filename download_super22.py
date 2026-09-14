import urllib.request
import ssl
import os

# Wir holen die Targets direkt von den ungesicherten Original-Quellen
TARGETS = {
    "Harman_IE_2019.csv": "https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/targets/Harman%20in-ear%202019v2.csv",
    "Super_22_Target.csv": "https://raw.githubusercontent.com/markusdredge/squiglink/master/targets/Super%2022.txt",
    "Super_22_Target_Alt.csv": "https://raw.githubusercontent.com/HiFiGo/squiglink/master/targets/Super%2022.txt"
}

OUT_DIR = os.path.join("reference_targets", "Pro_Live_IEMs")
os.makedirs(OUT_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("🚀 Lade Targets direkt von den originalen Reviewer-Quellen...")

for name, url in TARGETS.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
        
        out_path = os.path.join(OUT_DIR, name)
        with open(out_path, "w") as f:
            for line in data.strip().split('\n'):
                if "frequency" in line.lower() or not line.strip(): continue
                f.write(line.replace('\t', ',').replace(' ', ',') + "\n")
        print(f"✅ {name} erfolgreich gespeichert!")
    except Exception as e:
        print(f"❌ Fehler bei {name}: {e} (URL evtl. nicht mehr gültig)")

print("\nFertig! Die Dateien liegen jetzt in", OUT_DIR)
