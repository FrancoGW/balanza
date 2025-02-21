# mac_build.py
import PyInstaller.__main__
import os

# Obtener la ruta absoluta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, 'logo.png')

# Verificar si existe el logo
if not os.path.exists(logo_path):
    print("⚠️  Advertencia: No se encuentra logo.png en el directorio")

PyInstaller.__main__.run([
    'balanza_app.py',
    '--name=SistemaPesaje',
    '--windowed',
    '--onefile',
    '--clean',
    '--add-data=logo.png:.',
    '--icon=logo.png',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
])