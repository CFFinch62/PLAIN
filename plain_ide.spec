# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PLAIN IDE
Builds a standalone executable with all dependencies bundled
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root directory
project_root = Path('.').absolute()
plain_ide_dir = project_root / 'plain_ide'

# Collect all theme files
theme_datas = []
themes_dir = plain_ide_dir / 'themes' / 'syntax'
if themes_dir.exists():
    for conf_file in themes_dir.glob('*.conf'):
        theme_datas.append((str(conf_file), 'plain_ide/themes/syntax'))
    # Include README
    readme = themes_dir / 'README.md'
    if readme.exists():
        theme_datas.append((str(readme), 'plain_ide/themes/syntax'))
    # Include .gitkeep
    gitkeep = themes_dir / '.gitkeep'
    if gitkeep.exists():
        theme_datas.append((str(gitkeep), 'plain_ide/themes/syntax'))

# Collect images
images_dir = project_root / 'images'
if images_dir.exists():
    for img_file in images_dir.glob('*'):
        if img_file.is_file():
            theme_datas.append((str(img_file), 'images'))

# Collect interpreter binary
binaries = []
plain_exe = project_root / 'plain'
plain_exe_win = project_root / 'plain.exe'
if plain_exe.exists():
    binaries.append((str(plain_exe), '_internal'))  # Put in _internal folder
elif plain_exe_win.exists():
    binaries.append((str(plain_exe_win), '_internal'))  # Windows version

# Collect docs
docs_dir = project_root / 'docs'
if docs_dir.exists():
    for doc_file in docs_dir.glob('*.md'):
        theme_datas.append((str(doc_file), 'docs'))

a = Analysis(
    ['plain_ide/main.py'],
    pathex=[],
    binaries=binaries,
    datas=theme_datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'plain_ide.app.main_window',
        'plain_ide.app.settings',
        'plain_ide.app.themes',
        'plain_ide.app.editor',
        'plain_ide.app.syntax',
        'plain_ide.app.file_browser',
        'plain_ide.app.terminal',
        'plain_ide.app.debug_panel',
        'plain_ide.app.debug_manager',
        'plain_ide.app.find_replace',
        'plain_ide.app.settings_dialog',
        'plain_ide.app.help_viewer',
    ],
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
    [],
    exclude_binaries=True,
    name='plain-ide',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/favicon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='plain-ide',
)
