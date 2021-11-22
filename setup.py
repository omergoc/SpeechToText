from cx_Freeze import setup, Executable
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('App.py',  
    base=base,
    icon = "tht.ico" ) 
              ]

setup(
    name='THT Speech To Text // Beta',
    version = '0.1',
    description = 'PyQt5-ThtSpeechToText',
    options = dict(build_exe = buildOptions),
    executables = executables
    )