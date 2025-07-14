# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_all

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(SPEC))

# 收集所有数据文件
datas = []

# 添加资源文件
datas += [
    (os.path.join(project_root, 'resources'), 'resources'),
    (os.path.join(project_root, 'config'), 'config'),
    (os.path.join(project_root, 'examples'), 'examples'),
    (os.path.join(project_root, 'src'), 'src'),
]

# 收集PyQt6和相关包的数据文件
datas += collect_data_files('PyQt6')
datas += collect_data_files('PyQt6.QtWebEngineCore')

# 隐藏导入的模块
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'pandas',
    'numpy',
    'openpyxl',
    'json',
    'csv',
    'os',
    'sys',
    'traceback',
    'src.ui.main_window',
    'src.core.app_controller',
    'src.core.data_manager',
    'src.core.chart_renderer',
    'src.core.code_generator',
    'src.core.config_manager',
]

# 分析主程序
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 删除不需要的模块以减小文件大小
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChartsTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'resources', 'icons', 'app_icon.ico') if os.path.exists(os.path.join(project_root, 'resources', 'icons', 'app_icon.ico')) else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

# 创建分发目录 (可选，用于创建目录而不是单个exe)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='ChartsTools'
# ) 