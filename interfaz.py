from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QDialog, QMessageBox, QLabel, QHBoxLayout, QDateEdit, QInputDialog
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont
from logica import (
    registrar_transaccion, obtener_libro_diario, verificar_balance,
    inicializar_base_datos, obtener_libro_mayor, generar_pdf_libro_diario,
    generar_pdf_libro_mayor
)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Contabilidad")
        self.setGeometry(100, 100, 500, 400)

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

        contenedor = QWidget()
        layout = QVBoxLayout()

        btn_registrar_transaccion = QPushButton("Registrar Transacción", self)
        btn_registrar_transaccion.clicked.connect(self.abrir_formulario_transaccion)
        layout.addWidget(btn_registrar_transaccion)

        btn_ver_libro_diario = QPushButton("Ver Libro Diario", self)
        btn_ver_libro_diario.clicked.connect(self.ver_libro_diario)
        layout.addWidget(btn_ver_libro_diario)

        btn_ver_libro_mayor = QPushButton("Ver Libro Mayor", self)
        btn_ver_libro_mayor.clicked.connect(self.ver_libro_mayor)
        layout.addWidget(btn_ver_libro_mayor)

        btn_verificar_balance = QPushButton("Verificar Balance", self)
        btn_verificar_balance.clicked.connect(self.verificar_balance)
        layout.addWidget(btn_verificar_balance)

        btn_generar_pdf = QPushButton("Generar PDF (Libro diario)", self)
        btn_generar_pdf.clicked.connect(self.generar_pdf)
        layout.addWidget(btn_generar_pdf)

        btn_generar_pdf_mayor = QPushButton("Generar PDF (Libro Mayor)", self)
        btn_generar_pdf_mayor.clicked.connect(self.generar_pdf_libro_mayor)
        layout.addWidget(btn_generar_pdf_mayor)

        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def ver_libro_mayor(self):
        libro_mayor = obtener_libro_mayor()
        if not libro_mayor:
            QMessageBox.information(self, "Libro Mayor", "No hay cuentas registradas en el libro mayor.")
            return

        texto = "\n".join([f"{item['cuenta']}: {item['saldo']}" for item in libro_mayor])
        QMessageBox.information(self, "Libro Mayor", texto)

    def abrir_formulario_transaccion(self):
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

        self.input_fecha = QDateEdit(self.formulario)
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(QLabel("Fecha:"))
        layout.addWidget(self.input_fecha)

        layout.addWidget(QLabel("Cuentas y Montos (Debe):"))
        self.seccion_debe = QVBoxLayout()
        layout.addLayout(self.seccion_debe)
        self.agregar_campo_debe()

        btn_agregar_debe = QPushButton("Añadir campo Debe")
        btn_agregar_debe.clicked.connect(self.agregar_campo_debe)
        layout.addWidget(btn_agregar_debe)

        layout.addWidget(QLabel("Cuentas y Montos (Haber):"))
        self.seccion_haber = QVBoxLayout()
        layout.addLayout(self.seccion_haber)
        self.agregar_campo_haber()

        btn_agregar_haber = QPushButton("Añadir campo Haber")
        btn_agregar_haber.clicked.connect(self.agregar_campo_haber)
        layout.addWidget(btn_agregar_haber)

        self.input_descripcion = QLineEdit(self.formulario)
        self.input_descripcion.setPlaceholderText("Descripción")
        layout.addWidget(self.input_descripcion)

        btn_guardar = QPushButton("Guardar Transacción", self.formulario)
        btn_guardar.clicked.connect(self.guardar_transaccion)
        layout.addWidget(btn_guardar)

        self.formulario.setLayout(layout)
        self.formulario.exec_()

    def agregar_campo_debe(self):
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
        try:
            fecha = self.input_fecha.date().toString("yyyy-MM-dd")
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

    def generar_pdf(self):
        nombre_empresa, ok = QInputDialog.getText(self, "Nombre de la Empresa", "Ingrese el nombre de la empresa:")
        if not ok or not nombre_empresa:
            QMessageBox.warning(self, "Error", "Debe ingresar el nombre de la empresa.")
            return

        tasa_dolar, ok = QInputDialog.getDouble(
            self, "Tipo de Cambio", 
            "Ingrese el valor de 1 USD en Bs:",
            min=0.01, max=100000, decimals=2
        )
        if not ok or tasa_dolar <= 0:
            QMessageBox.warning(self, "Error", "Debe ingresar un tipo de cambio válido.")
            return

        # Diálogo para seleccionar el rango de fechas
        dialog_fechas = QDialog(self)
        dialog_fechas.setWindowTitle("Seleccionar Rango de Fechas")
        layout_fechas = QVBoxLayout()

        lbl_fecha_inicio = QLabel("Fecha de Inicio:")
        self.input_fecha_inicio = QDateEdit(dialog_fechas)
        self.input_fecha_inicio.setDate(QDate.currentDate())
        self.input_fecha_inicio.setCalendarPopup(True)
        self.input_fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        layout_fechas.addWidget(lbl_fecha_inicio)
        layout_fechas.addWidget(self.input_fecha_inicio)

        lbl_fecha_fin = QLabel("Fecha Final:")
        self.input_fecha_fin = QDateEdit(dialog_fechas)
        self.input_fecha_fin.setDate(QDate.currentDate())
        self.input_fecha_fin.setCalendarPopup(True)
        self.input_fecha_fin.setDisplayFormat("yyyy-MM-dd")
        layout_fechas.addWidget(lbl_fecha_fin)
        layout_fechas.addWidget(self.input_fecha_fin)

        btn_confirmar = QPushButton("Confirmar", dialog_fechas)
        btn_confirmar.clicked.connect(dialog_fechas.accept)
        layout_fechas.addWidget(btn_confirmar)

        dialog_fechas.setLayout(layout_fechas)

        if dialog_fechas.exec_() == QDialog.Accepted:
            fecha_inicio = self.input_fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.input_fecha_fin.date().toString("yyyy-MM-dd")

            if self.input_fecha_inicio.date() > self.input_fecha_fin.date():
                QMessageBox.warning(self, "Error", "La fecha de inicio debe ser menor o igual a la fecha de fin.")
                return

            libro_diario = obtener_libro_diario(fecha_inicio, fecha_fin)
            if not libro_diario:
                QMessageBox.warning(self, "Error", "No hay transacciones registradas en el rango de fechas seleccionado.")
                return

            try:
                pdf_path = generar_pdf_libro_diario(nombre_empresa, libro_diario, tasa_dolar, fecha_inicio, fecha_fin)
                QMessageBox.information(self, "Éxito", f"PDF generado correctamente: {pdf_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {str(e)}")

    def generar_pdf_libro_mayor(self):
        nombre_empresa, ok = QInputDialog.getText(self, "Nombre de la Empresa", "Ingrese el nombre de la empresa:")
        if not ok or not nombre_empresa:
            QMessageBox.warning(self, "Error", "Debe ingresar el nombre de la empresa.")
            return

        tasa_dolar, ok = QInputDialog.getDouble(
            self, "Tipo de Cambio", 
            "Ingrese el valor de 1 USD en Bs:",
            min=0.01, max=100000, decimals=2
        )
        if not ok or tasa_dolar <= 0:
            QMessageBox.warning(self, "Error", "Debe ingresar un tipo de cambio válido.")
            return

        try:
            pdf_path = generar_pdf_libro_mayor(nombre_empresa, tasa_dolar)
            QMessageBox.information(self, "Éxito", f"PDF del Libro Mayor generado correctamente: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {str(e)}")

def iniciar_interfaz():
    """
    Inicializa la interfaz de usuario.
    """
    inicializar_base_datos()
    app = QApplication([])
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec_()
