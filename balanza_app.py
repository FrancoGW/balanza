import sys
<<<<<<< HEAD
import os
import logging
from datetime import datetime
import sqlite3
import serial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QFileDialog, QHBoxLayout)
import pandas as pd
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

# Configurar logging12ß
log_file = os.path.expanduser('~/Desktop/balanza_log.txt')
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

class BalanzaApp(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            logging.info("Iniciando aplicación...")
            
            self.setWindowTitle("Sistema de Pesaje Industrial")
            self.setGeometry(100, 100, 800, 600)
            
            # Configurar ícono si existe
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logging.info("Ícono cargado correctamente")

            # Inicializar peso actual
            self.peso_actual = 0.0
            
            # Configurar la conexión serial USB
            self.setup_serial()
            
            # Configurar la base de datos
            self.setup_database()
            
            # Configurar la interfaz
            self.setup_ui()
            
            # Timer para actualizar el peso
            self.timer = QTimer()
            self.timer.timeout.connect(self.actualizar_peso)
            self.timer.start(1000)  # Actualizar cada segundo
            
            logging.info("Aplicación iniciada correctamente")
            
        except Exception as e:
            logging.error(f"Error en la inicialización: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al iniciar la aplicación: {str(e)}")
            raise

    def setup_serial(self):
        try:
            # Lista de posibles puertos USB en Mac
            possible_ports = [
                '/dev/tty.usbserial',
                '/dev/tty.usbmodem',
                '/dev/tty.wchusbserial'
            ]
            
            self.serial_port = None
            for port in possible_ports:
                try:
                    self.serial_port = serial.Serial(
                        port=port,
                        baudrate=9600,
                        timeout=1
                    )
                    logging.info(f"Conectado exitosamente al puerto {port}")
                    break
                except:
                    continue
            
            if self.serial_port is None:
                logging.warning("No se pudo conectar con la balanza - Modo simulación activado")
                
        except Exception as e:
            logging.error(f"Error al configurar puerto serial: {str(e)}")
            self.serial_port = None

    def setup_database(self):
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'registros_balanza.db')
            logging.info(f"Conectando a base de datos en: {db_path}")
            self.conn = sqlite3.connect(db_path)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pesajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora DATETIME NOT NULL,
                    peso REAL NOT NULL
                )
            ''')
            self.conn.commit()
            logging.info("Base de datos configurada correctamente")
        except Exception as e:
            logging.error(f"Error en setup_database: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error al configurar la base de datos: {str(e)}")
            raise

    def setup_ui(self):
        try:
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Display de peso actual
            self.peso_label = QLabel("Peso actual: 0.00 kg")
            self.peso_label.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin: 10px;
            """)
            layout.addWidget(self.peso_label)

            # Botón para guardar peso
            self.guardar_btn = QPushButton("Guardar Registro")
            self.guardar_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 5px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.guardar_btn.clicked.connect(self.guardar_registro)
            layout.addWidget(self.guardar_btn)

            # Tabla de registros
            self.tabla = QTableWidget()
            self.tabla.setColumnCount(3)
            self.tabla.setHorizontalHeaderLabels(["ID", "Fecha y Hora", "Peso (kg)"])
            self.tabla.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 5px;
                }
                QHeaderView::section {
                    background-color: #3498db;
                    color: white;
                    padding: 5px;
                }
            """)
            layout.addWidget(self.tabla)

            # Botones de exportación
            export_layout = QHBoxLayout()
            
            self.exportar_excel_btn = QPushButton("Exportar a Excel")
            self.exportar_excel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                    min-height: 40px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #219a52;
                }
            """)
            self.exportar_excel_btn.clicked.connect(self.exportar_excel)
            
            self.exportar_txt_btn = QPushButton("Exportar a TXT")
            self.exportar_txt_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                    min-height: 40px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #2472a4;
                }
            """)
            self.exportar_txt_btn.clicked.connect(self.exportar_txt)
            
            export_layout.addWidget(self.exportar_excel_btn)
            export_layout.addWidget(self.exportar_txt_btn)
            layout.addLayout(export_layout)

            # Estado de conexión
            self.estado_label = QLabel("Estado: " + 
                ("Conectado" if self.serial_port else "Modo simulación"))
            self.estado_label.setStyleSheet("""
                color: #7f8c8d;
                padding: 5px;
            """)
            layout.addWidget(self.estado_label)

            # Footer
            footer_label = QLabel("Develop by SFT DEV")
            footer_label.setStyleSheet("""
                color: #95a5a6;
                padding: 5px;
                font-size: 12px;
                font-style: italic;
                text-align: right;
            """)
            footer_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(footer_label)

            self.actualizar_tabla()
            logging.info("Interfaz configurada correctamente")
        except Exception as e:
            logging.error(f"Error en setup_ui: {str(e)}")
            raise

    def actualizar_peso(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                # Leer datos de la balanza
                self.serial_port.write(b'P\r\n')  # Comando para solicitar peso
                respuesta = self.serial_port.readline().decode().strip()
                try:
                    self.peso_actual = float(respuesta)
                except ValueError:
                    logging.warning(f"Respuesta no válida de la balanza: {respuesta}")
                    return
            else:
                # Modo simulación para pruebas
                import random
                self.peso_actual = random.uniform(1000, 5000)

            self.peso_label.setText(f"Peso actual: {self.peso_actual:.2f} kg")
            
        except Exception as e:
            logging.error(f"Error al actualizar peso: {str(e)}")
            self.peso_label.setText("Error de lectura")
            self.peso_actual = 0.0

    def guardar_registro(self):
        try:
=======
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
>>>>>>> b6afd05c46f834bf66b0543cc381be28fa6f9f12
            fecha_hora = datetime.now()
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO pesajes (fecha_hora, peso)
                VALUES (?, ?)
            ''', (fecha_hora, self.peso_actual))
            self.conn.commit()
            self.actualizar_tabla()
<<<<<<< HEAD
            
            QMessageBox.information(self, "Éxito", "Registro guardado correctamente")
            logging.info(f"Registro guardado: {self.peso_actual}kg en {fecha_hora}")
            
        except Exception as e:
            logging.error(f"Error al guardar registro: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error al guardar el registro: {str(e)}")

    def actualizar_tabla(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM pesajes ORDER BY fecha_hora DESC LIMIT 100')
            registros = cursor.fetchall()

            self.tabla.setRowCount(len(registros))
            for i, registro in enumerate(registros):
                self.tabla.setItem(i, 0, QTableWidgetItem(str(registro[0])))
                self.tabla.setItem(i, 1, QTableWidgetItem(str(registro[1])))
                self.tabla.setItem(i, 2, QTableWidgetItem(f"{registro[2]:.2f}"))
            
            # Ajustar el ancho de las columnas
            self.tabla.resizeColumnsToContents()
            
        except Exception as e:
            logging.error(f"Error al actualizar tabla: {str(e)}")

    def exportar_excel(self):
        try:
            # Obtener fecha actual para el nombre del archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"registros_pesaje_{fecha}.xlsx"
            
            # Abrir diálogo para guardar archivo
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Excel",
                nombre_archivo,
                "Excel Files (*.xlsx)"
            )
            
            if filepath:
                # Obtener todos los registros de la base de datos
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM pesajes ORDER BY fecha_hora DESC')
                registros = cursor.fetchall()
                
                # Crear DataFrame
                df = pd.DataFrame(registros, columns=['ID', 'Fecha y Hora', 'Peso (kg)'])
                
                # Guardar a Excel
                df.to_excel(filepath, index=False, sheet_name='Registros de Pesaje')
                
                QMessageBox.information(self, "Éxito", "Archivo Excel guardado correctamente")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a Excel: {str(e)}")
            logging.error(f"Error al exportar a Excel: {str(e)}")

    def exportar_txt(self):
        try:
            # Obtener fecha actual para el nombre del archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"registros_pesaje_{fecha}.txt"
            
            # Abrir diálogo para guardar archivo
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar TXT",
                nombre_archivo,
                "Text Files (*.txt)"
            )
            
            if filepath:
                # Obtener todos los registros de la base de datos
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM pesajes ORDER BY fecha_hora DESC')
                registros = cursor.fetchall()
                
                # Escribir al archivo
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("REGISTRO DE PESAJES\n")
                    f.write("==================\n\n")
                    for registro in registros:
                        f.write(f"ID: {registro[0]}\n")
                        f.write(f"Fecha y Hora: {registro[1]}\n")
                        f.write(f"Peso: {registro[2]:.2f} kg\n")
                        f.write("-" * 30 + "\n")
                
                QMessageBox.information(self, "Éxito", "Archivo TXT guardado correctamente")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a TXT: {str(e)}")
            logging.error(f"Error al exportar a TXT: {str(e)}")

    def closeEvent(self, event):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.conn.close()
            logging.info("Aplicación cerrada correctamente")
        except Exception as e:
            logging.error(f"Error al cerrar la aplicación: {str(e)}")

if __name__ == '__main__':
    try:
        logging.info("Iniciando QApplication")
        app = QApplication(sys.argv)
        window = BalanzaApp()
        window.show()
        logging.info("Ventana mostrada, iniciando loop principal")
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error fatal en la aplicación: {str(e)}")
        sys.exit(1)
=======

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
>>>>>>> b6afd05c46f834bf66b0543cc381be28fa6f9f12
