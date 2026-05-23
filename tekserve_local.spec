# PyInstaller spec for TekServe Local (Windows desktop build).
# Build: pyinstaller tekserve_local.spec --noconfirm
#
# AV / SmartScreen notes:
# - onedir (default here) is less likely to trigger heuristics than onefile
# - UPX compression is disabled (UPX often causes false positives)
# - Code signing (Authenticode) is the reliable way to avoid SmartScreen warnings

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")

hiddenimports = [
    "requests",
    "urllib3",
    "certifi",
    "charset_normalizer",
    "idna",
    "PIL._tkinter_finder",
    "server_core",
    "app_bundle",
    "web_server",
] + ctk_hiddenimports + collect_submodules("customtkinter")

excludes = [
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "pytest",
    "IPython",
    "notebook",
    "tkinter.test",
]

a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=ctk_binaries,
    datas=ctk_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TekServeLocal",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="version_info.txt" if sys.platform == "win32" else None,
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TekServeLocal",
)
