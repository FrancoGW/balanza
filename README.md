# Software de Control de Balanza

Sistema para control de pesaje industrial que permite:
- Lectura de peso en tiempo real desde balanza USB
- Almacenamiento de registros con fecha y hora
- Visualización de histórico de pesajes

## Requisitos
- Python 3.x
- PyQt6
- pyserial

## Instalación
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt