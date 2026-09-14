import os
import urllib.request
import ssl

TARGETS = {
    "IEF_Preference_2025.csv": "https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/targets/IEF%20Preference%202025.csv",
    "Harman_IE_2019v2.csv": "https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/targets/Harman%20in-ear%202019v2.csv",
    "IEF_Neutral_2023.csv": "https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/targets/IEF%20Neutral%202023.csv",
    "Diffuse_Field.csv": "https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/targets/Diffuse%20field.csv",
    "Free_Field.csv": "https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/targets/Free%20field.csv",
}

OUT_DIR = os.path.join("reference_targets", "Pro_Live_IEMs")
os.makedirs(OUT_DIR, exist_ok=True)

# Umgehe SSL-Fehler auf manchen Macs
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Lade Target Curves herunter...")

for filename, url in TARGETS.items():
    out_path = os.path.join(OUT_DIR, filename)
    print(f"Lade {filename} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = response.read().decode('utf-8')
            
            # Squiglink/AutoEQ nutzt manchmal Header wie "frequency,raw". Wir wandeln es für InEar Snitch um.
            lines = data.strip().split('\n')
            
            with open(out_path, "w") as f:
                for line in lines:
                    # Entferne Header
                    if "frequency" in line.lower():
                        continue
                    # Ersetze Trennzeichen (falls nötig)
                    clean_line = line.replace('\t', ',').replace(' ', ',')
                    f.write(clean_line + "\n")
                    
        print(f" -> Erfolgreich gespeichert!")
    except Exception as e:
        print(f" -> Fehler bei {filename}: {e}")

print("\nFertig! Starte InEar Snitch neu (oder klicke in Settings auf 'Reload Targets').")
