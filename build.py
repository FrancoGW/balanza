# build.py
import PyInstaller.__main__
import sys
import os

# Determinar el sistema operativo
is_windows = sys.platform.startswith('win')
is_mac = sys.platform.startswith('darwin')

# Nombre del archivo ejecutable
app_name = "Sistema de Pesaje"  # Cambia este nombre

# Configuración base
options = [
    'balanza_app.py',  # Tu archivo principal
    '--name=%s' % app_name,
    '--onefile',
    '--windowed',
    '--icon=logo.png',  # Tu archivo de ícono
    '--add-data=logo.png:.',  # Incluir el logo
]

# Configuración específica por sistema operativo
if is_windows:
    options.extend([
        '--add-binary=%s;.' % os.path.join('venv', 'Lib', 'site-packages', 'PyQt6', 'Qt6', 'bin', 'Qt6Core.dll'),
        '--add-binary=%s;.' % os.path.join('venv', 'Lib', 'site-packages', 'PyQt6', 'Qt6', 'bin', 'Qt6Gui.dll'),
        '--add-binary=%s;.' % os.path.join('venv', 'Lib', 'site-packages', 'PyQt6', 'Qt6', 'bin', 'Qt6Widgets.dll'),
    ])
elif is_mac:
    options.extend([
        '--target-architecture=x86_64',  # Para Mac Intel
        # '--target-architecture=arm64',  # Descomenta esta línea para Mac M1/M2
    ])

# Ejecutar PyInstaller
PyInstaller.__main__.run(options)