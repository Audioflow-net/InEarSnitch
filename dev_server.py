import os
import sys
import time
import subprocess

FILE_TO_WATCH = "metrology_lab.py"

def run_app():
    # Startet die App als Child-Process
    return subprocess.Popen([sys.executable, FILE_TO_WATCH])

if __name__ == "__main__":
    if not os.path.exists(FILE_TO_WATCH):
        print(f"Fehler: {FILE_TO_WATCH} nicht gefunden!")
        sys.exit(1)
        
    print(f"🚀 Starte InEar Snitch Live-Reload Server für {FILE_TO_WATCH}...")
    print("Drücke STRG+C um den Server zu beenden.\n")
    
    last_mtime = os.path.getmtime(FILE_TO_WATCH)
    process = run_app()
    
    try:
        while True:
            time.sleep(0.5) # Überprüfe alle 500ms
            current_mtime = os.path.getmtime(FILE_TO_WATCH)
            
            if current_mtime != last_mtime:
                print("🔄 Änderung erkannt! Lade GUI neu...")
                last_mtime = current_mtime
                process.terminate() # Alte Instanz abschießen
                process.wait()      # Kurz warten bis sie wirklich zu ist
                process = run_app() # Neue Instanz starten
                
    except KeyboardInterrupt:
        print("\n🛑 Beende Live-Reload Server.")
        process.terminate()
