#!/bin/bash
# build_mac.sh – InEar Snitch macOS App Builder
# Benutzt das venv Python mit PyInstaller 6.x
# Führe aus: bash /Users/ben/Desktop/InEarSnitch/build_mac.sh

set -e  # Exit on error

SCRIPT_DIR="/Users/ben/Desktop/InEarSnitch"
PYTHON="$SCRIPT_DIR/venv/bin/python3"
PYINSTALLER="$SCRIPT_DIR/venv/bin/pyinstaller"
DIST="$SCRIPT_DIR/dist/InEarSnitch.app"
PLIST="$DIST/Contents/Info.plist"

echo "╔══════════════════════════════════════════════════════╗"
echo "║         InEar Snitch – macOS App Builder             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "► Python:       $PYTHON"
echo "► PyInstaller:  $($PYTHON -m PyInstaller --version)"
echo ""

# Schritt 1: Altes Build-Artefakt bereinigen
echo "▶ Schritt 1: Bereinige alte Build-Artefakte..."
rm -rf "$SCRIPT_DIR/build" "$SCRIPT_DIR/dist"
echo "  ✓ Bereinigt"

# Schritt 2: .DS_Store Dateien entfernen (brechen codesign!)
echo "▶ Schritt 2: Entferne .DS_Store Dateien..."
find "$SCRIPT_DIR" -name ".DS_Store" -delete 2>/dev/null || true
echo "  ✓ .DS_Store entfernt"

# Schritt 3: PyInstaller Build
echo "▶ Schritt 3: PyInstaller Build starten..."
"$PYTHON" -m PyInstaller \
    --noconfirm \
    "$SCRIPT_DIR/InEarSnitch.spec"

echo ""
echo "  ✓ Build abgeschlossen"

# Schritt 4: Info.plist prüfen (NSMicrophoneUsageDescription sollte bereits im spec definiert sein)
echo "▶ Schritt 4: Prüfe Info.plist..."
if [ -f "$PLIST" ]; then
    if /usr/libexec/PlistBuddy -c "Print :NSMicrophoneUsageDescription" "$PLIST" &>/dev/null; then
        echo "  ✓ NSMicrophoneUsageDescription: OK"
    else
        echo "  ⚠ NSMicrophoneUsageDescription fehlt – füge es hinzu..."
        plutil -insert NSMicrophoneUsageDescription \
            -string "InEar Snitch requires microphone access to measure IEM frequency responses via the IEC 711 coupler." \
            "$PLIST"
        echo "  ✓ Hinzugefügt"
    fi
else
    echo "  ✗ FEHLER: Info.plist nicht gefunden! Build fehlgeschlagen."
    exit 1
fi

# Schritt 5: Erweiterte Attribute bereinigen (verhindert "App ist beschädigt" Meldung)
echo "▶ Schritt 5: Bereinige Extended Attributes..."
xattr -cr "$DIST"
echo "  ✓ Extended Attributes bereinigt"

# Schritt 6: Quick-Test ob die Binary startet
echo "▶ Schritt 6: Quick Import-Test..."
"$PYTHON" -c "import PySide6, numpy, scipy, sounddevice, pyqtgraph; print('  ✓ Alle Core-Module importierbar')"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  BUILD ERFOLGREICH!                              ║"
echo "║                                                      ║"
echo "║  App: dist/InEarSnitch.app                          ║"
echo "║  Doppelklick oder:                                   ║"
echo "║  open dist/InEarSnitch.app                          ║"
echo "╚══════════════════════════════════════════════════════╝"
