from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QDialog, QMessageBox, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QFont
from logica import registrar_transaccion, obtener_libro_diario, verificar_balance, inicializar_base_datos


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Contabilidad")
        self.setGeometry(100, 100, 500, 400)

        # Estilo general
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f4f8;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #004a99;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                font-weight: bold;
            }
        """)

        # Contenedor principal
        contenedor = QWidget()
        layout = QVBoxLayout()

        # Botones
        btn_registrar_transaccion = QPushButton("Registrar Transacción", self)
        btn_registrar_transaccion.clicked.connect(self.abrir_formulario_transaccion)
        layout.addWidget(btn_registrar_transaccion)

        btn_ver_libro_diario = QPushButton("Ver Libro Diario", self)
        btn_ver_libro_diario.clicked.connect(self.ver_libro_diario)
        layout.addWidget(btn_ver_libro_diario)

        btn_verificar_balance = QPushButton("Verificar Balance", self)
        btn_verificar_balance.clicked.connect(self.verificar_balance)
        layout.addWidget(btn_verificar_balance)

        # Configuración final
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def abrir_formulario_transaccion(self):
        """Abre un formulario para registrar una transacción."""
        self.formulario = QDialog()
        self.formulario.setWindowTitle("Registrar Transacción")
        layout = QVBoxLayout()

        self.formulario.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #004a99;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                font-weight: bold;
            }
        """)

        self.campos_debe = []
        self.campos_haber = []

        # Fecha
        self.input_fecha = QLineEdit(self.formulario)
        self.input_fecha.setPlaceholderText("Fecha (AAAA-MM-DD)")
        layout.addWidget(self.input_fecha)

        # Sección Debe
        layout.addWidget(QLabel("Cuentas y Montos (Debe):"))
        self.seccion_debe = QVBoxLayout()
        layout.addLayout(self.seccion_debe)
        self.agregar_campo_debe()

        btn_agregar_debe = QPushButton("Añadir campo Debe")
        btn_agregar_debe.clicked.connect(self.agregar_campo_debe)
        layout.addWidget(btn_agregar_debe)

        # Sección Haber
        layout.addWidget(QLabel("Cuentas y Montos (Haber):"))
        self.seccion_haber = QVBoxLayout()
        layout.addLayout(self.seccion_haber)
        self.agregar_campo_haber()

        btn_agregar_haber = QPushButton("Añadir campo Haber")
        btn_agregar_haber.clicked.connect(self.agregar_campo_haber)
        layout.addWidget(btn_agregar_haber)

        # Descripción
        self.input_descripcion = QLineEdit(self.formulario)
        self.input_descripcion.setPlaceholderText("Descripción")
        layout.addWidget(self.input_descripcion)

        # Botón Guardar
        btn_guardar = QPushButton("Guardar Transacción", self.formulario)
        btn_guardar.clicked.connect(self.guardar_transaccion)
        layout.addWidget(btn_guardar)

        self.formulario.setLayout(layout)
        self.formulario.exec_()

    def agregar_campo_debe(self):
        """Añade un nuevo campo para Debe."""
        layout = QHBoxLayout()
        cuenta = QLineEdit()
        cuenta.setPlaceholderText("Cuenta (Debe)")
        monto = QLineEdit()
        monto.setPlaceholderText("Monto (Debe)")
        self.campos_debe.append((cuenta, monto))
        layout.addWidget(cuenta)
        layout.addWidget(monto)
        self.seccion_debe.addLayout(layout)

    def agregar_campo_haber(self):
        """Añade un nuevo campo para Haber."""
        layout = QHBoxLayout()
        cuenta = QLineEdit()
        cuenta.setPlaceholderText("Cuenta (Haber)")
        monto = QLineEdit()
        monto.setPlaceholderText("Monto (Haber)")
        self.campos_haber.append((cuenta, monto))
        layout.addWidget(cuenta)
        layout.addWidget(monto)
        self.seccion_haber.addLayout(layout)

    def guardar_transaccion(self):
        """Guarda la transacción ingresada."""
        try:
            fecha = self.input_fecha.text()
            cuentas_debe = [campo[0].text() for campo in self.campos_debe if campo[0].text()]
            montos_debe = [float(campo[1].text()) for campo in self.campos_debe if campo[1].text()]
            cuentas_haber = [campo[0].text() for campo in self.campos_haber if campo[0].text()]
            montos_haber = [float(campo[1].text()) for campo in self.campos_haber if campo[1].text()]
            descripcion = self.input_descripcion.text()

            if registrar_transaccion(fecha, cuentas_debe, montos_debe, cuentas_haber, montos_haber, descripcion):
                QMessageBox.information(self.formulario, "Éxito", "Transacción registrada con éxito.")
                self.formulario.close()
            else:
                QMessageBox.warning(self.formulario, "Error", "Los montos de Debe y Haber no coinciden.")
        except ValueError:
            QMessageBox.warning(self.formulario, "Error", "Debe ingresar valores numéricos válidos.")

    def ver_libro_diario(self):
        libro_diario = obtener_libro_diario()
        texto = "\n".join(
            f"{t['fecha']} | Debe: {', '.join(t['cuentas_debe'])} ({sum(t['montos_debe'])}) | "
            f"Haber: {', '.join(t['cuentas_haber'])} ({sum(t['montos_haber'])}) | {t['descripcion']}"
            for t in libro_diario
        )
        QMessageBox.information(self, "Libro Diario", texto or "No hay transacciones registradas.")

    def verificar_balance(self):
        balance = verificar_balance()
        texto = (
            f"Total Debe: {balance['total_debe']}\n"
            f"Total Haber: {balance['total_haber']}\n\n"
        )
        texto += "El balance está equilibrado." if balance["equilibrado"] else "El balance no está equilibrado."
        QMessageBox.information(self, "Verificar Balance", texto)


def iniciar_interfaz():
    """
    Inicializa la interfaz de usuario.
    """
    inicializar_base_datos()
    app = QApplication([])
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec_()
