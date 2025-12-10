# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_dynamic_libs,
    collect_data_files,
    collect_submodules,
)

block_cipher = None

# Use current working directory as project root
project_root = Path(".").resolve()
prompts_dir = project_root / "prompts"

# ---------- data files ----------
# Explicitly add each prompt file so they are definitely bundled
datas = [
    (str(prompts_dir / "pj_old.txt"), "prompts"),
    (str(prompts_dir / "vc.txt"), "prompts"),
    (str(prompts_dir / "pv.txt"), "prompts"),
    (str(prompts_dir / "reclass.txt"), "prompts"),
    (str(prompts_dir / "ujd.txt"), "prompts"),
    (str(prompts_dir / "tll.txt"), "prompts"),
    (str(prompts_dir / "unknown.txt"), "prompts"),
    (str(prompts_dir / "final_report.txt"), "prompts"),
]

# ctransformers data files (vocab, configs, etc.)
datas += collect_data_files("ctransformers")

# ---------- native libs ----------
# This collects libctransformers.dylib and other native libs
binaries = collect_dynamic_libs("ctransformers")

# ---------- hidden imports ----------
hiddenimports = (
    collect_submodules("backend")
    + collect_submodules("ctransformers")
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
