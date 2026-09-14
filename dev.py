import os
import sys
import time
import subprocess

def get_mtimes():
    """Gibt ein Dictionary mit den letzten Änderungsdaten aller Python-Dateien zurück."""
    mtimes = {}
    for root, _, files in os.walk('.'):
        # Ignoriere virtuelle Umgebungen, Git und Cache-Ordner
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for f in files:
            # Nur echte App-Dateien überwachen, keine temporären Fix/Patch-Skripte
            if f.endswith('.py') and f not in ['dev.py', 'setup.py']:
                if f.startswith('fix_') or f.startswith('patch_') or f.startswith('test_'):
                    continue
                path = os.path.join(root, f)
                mtimes[path] = os.path.getmtime(path)
    return mtimes

def main():
    print("🚀 Starte InEar Snitch Live-Reload Server...")
    print("Die App startet jetzt automatisch neu, sobald Code geändert wird!")
    
    # Starte die eigentliche App
    process = subprocess.Popen([sys.executable, "main.py"])
    last_mtimes = get_mtimes()
    
    try:
        while True:
            time.sleep(1)
            current_mtimes = get_mtimes()
            
            # Prüfe, ob sich eine Datei geändert hat (z.B. weil ein Agent Code geschrieben hat)
            if current_mtimes != last_mtimes:
                print("\n🔄 Datei-Änderung erkannt! Starte App neu...\n")
                process.terminate() # Schließe die alte App
                process.wait()      # Warte bis sie wirklich zu ist
                
                # Starte die App frisch
                process = subprocess.Popen([sys.executable, "main.py"])
                last_mtimes = current_mtimes
                
    except KeyboardInterrupt:
        # Wenn der User im Terminal Strg+C drückt
        process.terminate()
        print("\n👋 Live-Reload beendet.")

if __name__ == "__main__":
    main()
