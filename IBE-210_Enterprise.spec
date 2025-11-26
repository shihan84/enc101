# -*- mode: python ; coding: utf-8 -*-
# IBE-210 v2.1.0 Enterprise Build Specification
# Includes bundled TSDuck support

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect all source files
src_path = Path('src')
# Note: Don't add Python source files to datas - PyInstaller includes them automatically via imports
datas = [
    ('logo.png', '.'),
    ('logo.ico', '.'),
    ('scte35_final', 'scte35_final'),
    ('config', 'config'),
    ('profiles', 'profiles'),
]

# Add TSDuck binaries if they exist (bundled TSDuck support)
tsduck_bin = Path('tsduck/bin')
tsduck_plugins = Path('tsduck/plugins')
tsduck_libs = Path('tsduck/libs')

if tsduck_bin.exists():
    datas.append(('tsduck/bin', 'tsduck/bin'))
    print(f"[INFO] Including bundled TSDuck binaries from: {tsduck_bin}")

if tsduck_plugins.exists():
    datas.append(('tsduck/plugins', 'tsduck/plugins'))
    print(f"[INFO] Including bundled TSDuck plugins from: {tsduck_plugins}")

if tsduck_libs.exists():
    datas.append(('tsduck/libs', 'tsduck/libs'))
    print(f"[INFO] Including bundled TSDuck libraries from: {tsduck_libs}")

# Collect all submodules automatically
src_submodules = collect_submodules('src')
services_submodules = collect_submodules('src.services')
models_submodules = collect_submodules('src.models')
ui_submodules = collect_submodules('src.ui')
widgets_submodules = collect_submodules('src.ui.widgets')

# Add all Python files from src directory
hiddenimports = [
    'src',
    # Core modules
    'src.core',
    'src.core.application',
    'src.core.config',
    'src.core.logger',
    # Services - use collected submodules
    'src.services',
    'src.services.tsduck_service',
    'src.services.stream_service',
    'src.services.scte35_service',
    'src.services.scte35_monitor_service',
    'src.services.dynamic_marker_service',
    'src.services.telegram_service',
    'src.services.monitoring_service',
    'src.services.profile_service',
    'src.services.stream_analyzer_service',
    'src.services.bitrate_monitor_service',
    'src.services.epg_service',
    # Models
    'src.models',
    'src.models.stream_config',
    'src.models.scte35_marker',
    'src.models.profile',
    'src.models.session',
    # UI
    'src.ui',
    'src.ui.main_window',
    'src.ui.widgets',
    'src.ui.widgets.stream_config_widget',
    'src.ui.widgets.scte35_widget',
    'src.ui.widgets.scte35_monitor_widget',
    'src.ui.widgets.monitoring_widget',
    'src.ui.widgets.dashboard_widget',
    'src.ui.widgets.stream_quality_widget',
    'src.ui.widgets.bitrate_monitor_widget',
    'src.ui.widgets.epg_editor_widget',
    # Database
    'src.database',
    'src.database.database',
    # API
    'src.api',
    'src.api.server',
    'src.api.routes',
    # Utils
    'src.utils',
    'src.utils.validators',
    'src.utils.helpers',
    'src.utils.exceptions',
    'src.utils.crash_handler',
    # External dependencies
    'cryptography',
    'cryptography.fernet',
    'psutil',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
] + src_submodules + services_submodules + models_submodules + ui_submodules + widgets_submodules

a = Analysis(
    ['main_enterprise.py'],
    pathex=[str(Path('.').absolute()), str(Path('src').absolute())],  # Add current dir and src to path
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
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
    name='IBE-210_Enterprise',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(Path('logo.ico').absolute()) if Path('logo.ico').exists() else None,
    version=str(Path('version_info.txt').absolute()) if Path('version_info.txt').exists() else None,
)

