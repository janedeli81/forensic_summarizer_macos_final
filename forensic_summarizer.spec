# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_dynamic_libs,
    collect_data_files,
    collect_submodules,
)

block_cipher = None

project_root = Path(__file__).resolve().parent

# Data files: prompts + data files from ctransformers (if any)
datas = [
    # All prompt templates
    (str(project_root / "prompts"), "prompts"),
]

# Include any non-binary data shipped with ctransformers
datas += collect_data_files("ctransformers")

# Native libraries for ctransformers (this is what was missing on the client's Mac)
binaries = collect_dynamic_libs("ctransformers")

# Make sure all backend and ctransformers submodules are included
hiddenimports = collect_submodules("backend") + collect_submodules("ctransformers")

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
