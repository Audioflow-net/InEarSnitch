# -*- mode: python ; coding: utf-8 -*-
# InEarSnitch.spec – Cross-Platform (macOS .app + Windows .exe)
# PyInstaller 6.x
#
# SPECPATH wird von PyInstaller automatisch auf den Ordner dieser Datei gesetzt.
# Dadurch funktioniert das Spec auf macOS, Windows und im GitHub Actions CI.

import os
import sys

# SPECPATH ist eine eingebaute PyInstaller-Variable (Verzeichnis dieser .spec-Datei)
PROJECT_DIR = SPECPATH  # noqa: F821 – von PyInstaller bereitgestellt

# ─── ICONS ─────────────────────────────────────────────────────────────────────
ICON_ICNS = os.path.join(PROJECT_DIR, 'icon.icns')   # macOS
ICON_ICO  = os.path.join(PROJECT_DIR, 'icon.ico')    # Windows
ICON = ICON_ICNS if sys.platform == 'darwin' else ICON_ICO

# ─── DATA FILES ────────────────────────────────────────────────────────────────
datas = [
    # Handbücher
    (os.path.join(PROJECT_DIR, 'manual_de.md'), '.'),
    (os.path.join(PROJECT_DIR, 'manual_en.md'), '.'),
    (os.path.join(PROJECT_DIR, 'manual_es.md'), '.'),
    # Reference Targets (kompletter Ordner)
    (os.path.join(PROJECT_DIR, 'reference_targets'), 'reference_targets'),
    # Werksmäßige Mikrofonkalibrierungen
    (os.path.join(PROJECT_DIR, 'calibrations'), 'calibrations'),
]

# ─── HIDDEN IMPORTS ────────────────────────────────────────────────────────────
hiddenimports = [
    # PySide6
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtMultimedia',
    'PySide6.QtOpenGL',
    'PySide6.QtPrintSupport',
    'PySide6.QtSvg',
    'PySide6.QtXml',
    # pyqtgraph
    'pyqtgraph',
    'pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu',
    'pyqtgraph.graphicsItems.GradientEditorItem',
    'pyqtgraph.graphicsItems.ROI',
    'pyqtgraph.graphicsItems.InfiniteLine',
    'pyqtgraph.graphicsItems.LinearRegionItem',
    'pyqtgraph.graphicsItems.TextItem',
    'pyqtgraph.opengl',
    'pyqtgraph.Qt',
    # numpy / scipy
    'numpy',
    'numpy.core._multiarray_umath',
    'numpy.fft',
    'numpy.linalg',
    'numpy.random',
    'scipy',
    'scipy.fft',
    'scipy.signal',
    'scipy.signal.windows',
    'scipy.stats',
    'scipy.interpolate',
    'scipy.linalg',
    # sounddevice
    'sounddevice',
    # packaging / setuptools
    'packaging',
    'packaging.version',
    'packaging.requirements',
    'packaging.specifiers',
    # SQLite
    'sqlite3',
    '_sqlite3',
    # stdlib
    'json', 'csv', 'math', 'time', 'traceback', 'shutil', 'glob',
    # Lokale App-Module
    'theme',
    'analysis',
    'analysis_ui',
    'audio_engine',
    'calibration_ui',
    'config',
    'database',
    'dialogs',
    'eq_math',
    'history_ui',
    'profile_ui',
    'spl_cal_ui',
    'tour_ui',
]

# ─── ANALYSIS ──────────────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'PIL', 'cv2', 'OpenGL',
        'trimesh', 'pillow_heif', 'PyQt5', 'PyQt6',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)  # noqa: F821

# ─── EXE ───────────────────────────────────────────────────────────────────────
exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='InEarSnitch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,        # --windowed: kein Konsolfenster
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows-Icon (optional – liegt im Projektordner wenn vorhanden)
    icon=ICON if os.path.exists(ICON) else None,
)

# ─── COLLECT ───────────────────────────────────────────────────────────────────
coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='InEarSnitch',
)

# ─── APP BUNDLE (nur macOS) ────────────────────────────────────────────────────
if sys.platform == 'darwin':
    app = BUNDLE(  # noqa: F821
        coll,
        name='InEarSnitch.app',
        icon=ICON_ICNS if os.path.exists(ICON_ICNS) else None,
        bundle_identifier='com.inearsnitch.app',
        info_plist={
            'NSMicrophoneUsageDescription':
                'InEar Snitch requires microphone access to measure IEM frequency responses via the IEC 711 coupler.',
            'CFBundleName': 'InEar SNITCH',
            'CFBundleDisplayName': 'InEar SNITCH',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'LSMinimumSystemVersion': '12.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
    )
