# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('images', 'images'), ('qml', 'qml'), ('config.json', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='LCDP - Inventorist App',
          debug=False, # Set to True for debug
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False, # Set to True for debug
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          icon='images/icon.ico',
          entitlements_file=None )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='LCDP - Inventorist App')
app = BUNDLE(coll,
             name='LCDP - Inventorist App.app',
             version=os.getenv("GITHUB_REF_NAME", "v0.0.0"),
             icon='images/icon.ico',
             bundle_identifier=None)
