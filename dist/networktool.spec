# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# if you really want to figure out every lib that is needed then follow this: https://blog.csdn.net/qq_41730930/article/details/112612864

a = Analysis(['main.py', 'tests.py', 'util.py'],
             pathex=['R:\\project\\networkTool'],
             binaries=[],
             datas=[('iperf/*', 'iperf'),
			 ('ookla/*', 'ookla'),
			 ('resources/*', 'resources'),
             (r'C:\Users\marc_\AppData\Local\Programs\Python\Python39\Lib\site-packages\PyQt6\Qt6\plugins\platforms', 'platforms'),  # required because pyinstaller doesn't recognize pyqt6 yet. https://stackoverflow.com/questions/66286229/create-pyqt6-python-project-executable
             (r'C:\Users\marc_\AppData\Local\Programs\Python\Python39\Lib\site-packages\PyQt6\sip.cp39-win_amd64.pyd', 'PyQt6/sip.pyd'), # https://github.com/pyinstaller/pyinstaller/issues/5414
             (r'C:\Users\marc_\AppData\Local\Programs\Python\Python39\Lib\site-packages\PyQt6\Qt6', 'PyQt6/Qt6') # https://github.com/pyinstaller/pyinstaller/issues/5414
             ],
             hiddenimports=["PyQt6.sip"], # https://github.com/pyinstaller/pyinstaller/issues/5414
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
          name='networktool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
		  icon='networktool.ico', # I created the icon from a png with https://www.zamzar.com/convert/png-to-ico/
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='networktool')
