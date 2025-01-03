from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QDialog, QMessageBox
)
from logica import registrar_transaccion, obtener_libro_diario, verificar_balance


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Contabilidad")
        self.setGeometry(100, 100, 400, 300)

        # Contenedor principal
        contenedor = QWidget()
        layout = QVBoxLayout()

        # Botón: Registrar Transacción
        btn_registrar_transaccion = QPushButton("Registrar Transacción", self)
        btn_registrar_transaccion.clicked.connect(self.abrir_formulario_transaccion)
        layout.addWidget(btn_registrar_transaccion)

        # Botón: Ver Libro Diario
        btn_ver_libro_diario = QPushButton("Ver Libro Diario", self)
        btn_ver_libro_diario.clicked.connect(self.ver_libro_diario)
        layout.addWidget(btn_ver_libro_diario)

        # Botón: Verificar Balance
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

        self.input_fecha = QLineEdit(self.formulario)
        self.input_fecha.setPlaceholderText("Fecha (AAAA-MM-DD)")
        layout.addWidget(self.input_fecha)

        self.input_cuenta_debe = QLineEdit(self.formulario)
        self.input_cuenta_debe.setPlaceholderText("Cuenta (Debe)")
        layout.addWidget(self.input_cuenta_debe)

        self.input_monto_debe = QLineEdit(self.formulario)
        self.input_monto_debe.setPlaceholderText("Monto (Debe)")
        layout.addWidget(self.input_monto_debe)

        self.input_cuenta_haber = QLineEdit(self.formulario)
        self.input_cuenta_haber.setPlaceholderText("Cuenta (Haber)")
        layout.addWidget(self.input_cuenta_haber)

        self.input_monto_haber = QLineEdit(self.formulario)
        self.input_monto_haber.setPlaceholderText("Monto (Haber)")
        layout.addWidget(self.input_monto_haber)

        self.input_descripcion = QLineEdit(self.formulario)
        self.input_descripcion.setPlaceholderText("Descripción")
        layout.addWidget(self.input_descripcion)

        btn_guardar = QPushButton("Guardar Transacción", self.formulario)
        btn_guardar.clicked.connect(self.guardar_transaccion)
        layout.addWidget(btn_guardar)

        self.formulario.setLayout(layout)
        self.formulario.exec_()

    def guardar_transaccion(self):
        """Guarda la transacción ingresada en el formulario."""
        try:
            fecha = self.input_fecha.text()
            cuenta_debe = self.input_cuenta_debe.text()
            monto_debe = float(self.input_monto_debe.text())
            cuenta_haber = self.input_cuenta_haber.text()
            monto_haber = float(self.input_monto_haber.text())
            descripcion = self.input_descripcion.text()

            if registrar_transaccion(fecha, cuenta_debe, monto_debe, cuenta_haber, monto_haber, descripcion):
                QMessageBox.information(self.formulario, "Éxito", "Transacción registrada con éxito")
                self.formulario.close()
            else:
                QMessageBox.warning(self.formulario, "Error", "Los datos ingresados son incorrectos.")
        except ValueError:
            QMessageBox.warning(self.formulario, "Error", "Debe ingresar valores numéricos válidos para los montos.")

    def ver_libro_diario(self):
        """Muestra el libro diario en un cuadro de diálogo."""
        libro_diario = obtener_libro_diario()
        if not libro_diario:
            QMessageBox.information(self, "Libro Diario", "No hay transacciones registradas.")
        else:
            texto = "\n".join(
                f"{t['fecha']} | Debe: {t['cuenta_debe']} ({t['monto_debe']}) | "
                f"Haber: {t['cuenta_haber']} ({t['monto_haber']}) | {t['descripcion']}"
                for t in libro_diario
            )
            QMessageBox.information(self, "Libro Diario", texto)

    def verificar_balance(self):
        """Muestra el estado del balance contable."""
        balance = verificar_balance()
        texto = (
            f"Total Debe: {balance['total_debe']}\n"
            f"Total Haber: {balance['total_haber']}\n\n"
        )
        if balance["equilibrado"]:
            texto += "El balance está equilibrado."
        else:
            texto += "El balance no está equilibrado."
        QMessageBox.information(self, "Verificar Balance", texto)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
