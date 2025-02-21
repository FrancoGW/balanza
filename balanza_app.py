import sys
import sqlite3
from datetime import datetime
import serial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import QTimer

class BalanzaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SFT DEV - Sistema de Pesaje")  # Cambia este título
        
        # Configurar ícono de la aplicación
        from PyQt6.QtGui import QIcon
        self.setWindowIcon(QIcon('logo.png'))  # Asegúrate de tener un archivo logo.png
        self.setGeometry(100, 100, 800, 600)
        
        # Configurar la conexión serial USB
        try:
            self.serial_port = serial.Serial(
                port='COM3',  # Ajustar según el puerto USB
                baudrate=9600,
                timeout=1
            )
        except serial.SerialException:
            print("Error: No se pudo conectar con la balanza")
            self.serial_port = None

        # Configurar la base de datos
        self.setup_database()
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Timer para actualizar el peso
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_peso)
        self.timer.start(1000)  # Actualizar cada segundo

    def setup_database(self):
        self.conn = sqlite3.connect('registros_balanza.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME NOT NULL,
                peso REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Display de peso actual
        self.peso_label = QLabel("Peso actual: 0.00 kg")
        self.peso_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.peso_label)

        # Botón para guardar peso
        self.guardar_btn = QPushButton("Guardar Registro")
        self.guardar_btn.clicked.connect(self.guardar_registro)
        layout.addWidget(self.guardar_btn)

        # Tabla de registros
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Fecha y Hora", "Peso (kg)"])
        layout.addWidget(self.tabla)

        # Cargar registros existentes
        self.actualizar_tabla()

    def actualizar_peso(self):
        if self.serial_port:
            try:
                # Leer datos de la balanza
                # Nota: Este código debe ajustarse según el protocolo específico de tu balanza
                self.serial_port.write(b'P\r\n')  # Comando para solicitar peso
                respuesta = self.serial_port.readline().decode().strip()
                
                # Procesar la respuesta según el formato de tu balanza
                # Este es un ejemplo, ajustar según corresponda
                peso = float(respuesta)
                self.peso_label.setText(f"Peso actual: {peso:.2f} kg")
                self.peso_actual = peso
            except:
                self.peso_label.setText("Error de lectura")
                self.peso_actual = 0.0

    def guardar_registro(self):
        if hasattr(self, 'peso_actual'):
            fecha_hora = datetime.now()
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO pesajes (fecha_hora, peso)
                VALUES (?, ?)
            ''', (fecha_hora, self.peso_actual))
            self.conn.commit()
            self.actualizar_tabla()

    def actualizar_tabla(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pesajes ORDER BY fecha_hora DESC LIMIT 100')
        registros = cursor.fetchall()

        self.tabla.setRowCount(len(registros))
        for i, registro in enumerate(registros):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(registro[0])))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(registro[1])))
            self.tabla.setItem(i, 2, QTableWidgetItem(f"{registro[2]:.2f}"))

    def closeEvent(self, event):
        if self.serial_port:
            self.serial_port.close()
        self.conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BalanzaApp()
    window.show()
    sys.exit(app.exec())
