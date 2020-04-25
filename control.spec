# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['control.py'],
             pathex=['/Users/phakawat/Desktop/mt-senior-project'],
             binaries=[],
             datas=[('subjects/*', 'subjects')],
             hiddenimports=[],
             hookspath=[],
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
          name='control',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='whale.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='control')
app = BUNDLE(coll,
             name='control.app',
             
             bundle_identifier=None,info_plist={
                 "NSHighResolutionCapable":'True'
             })
