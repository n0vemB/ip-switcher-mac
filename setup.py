from setuptools import setup

APP = ['network_switcher.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # 禁用argv_emulation来避免Carbon框架问题
    'plist': {
        'LSUIElement': False,
        'CFBundleName': "网络设置切换器",
        'CFBundleDisplayName': "网络设置切换器",
        'CFBundleGetInfoString': "网络IP设置切换工具",
        'CFBundleIdentifier': "com.networkswitcher.app",
        'CFBundleVersion': "1.1.0",
        'CFBundleShortVersionString': "1.1.0",
        'NSHumanReadableCopyright': "Copyright © 2024, Network Switcher, All Rights Reserved",
        'LSApplicationCategoryType': 'public.app-category.utilities'
    },
    'iconfile': 'app.icns',
    'includes': ['tkinter'],
    'excludes': ['PyQt4', 'PyQt5', 'PyQt6', 'PySide', 'PySide2', 'PySide6', 'setuptools', 'numpy', 'scipy', 'matplotlib'],
    'packages': [],
    'strip': True,
    'optimize': 2,
    'no_chdir': True
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)