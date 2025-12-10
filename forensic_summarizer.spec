# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_dynamic_libs,
    collect_data_files,
    collect_submodules,
)

block_cipher = None

# У .spec файлі використовуємо поточну директорію, а не __file__
project_root = Path(".").resolve()

# ---------- data files ----------
datas = [
    # Вся папка prompts цілком
    (str(project_root / "prompts"), "prompts"),
]

# Дані самого ctransformers (словники, конфіги і т.п.)
datas += collect_data_files("ctransformers")

# ---------- native libs ----------
# Тут якраз збираються libctransformers.dylib та інші
binaries = collect_dynamic_libs("ctransformers")

# ---------- hidden imports ----------
hiddenimports = (
    collect_submodules("backend") +
    collect_submodules("ctransformers")
)

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='forensic_summarizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='forensic_summarizer.app',
    icon=None,
    bundle_identifier='com.yourdomain.forensic_summarizer',
)
