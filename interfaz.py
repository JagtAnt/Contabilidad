from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QDialog, QMessageBox, QLabel, QHBoxLayout, QDateEdit, 
    QInputDialog, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from logica import (
    registrar_transaccion, obtener_libro_diario, verificar_balance,
    inicializar_base_datos, obtener_libro_mayor, generar_pdf_libro_diario, generar_pdf_libro_mayor
)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Contabilidad")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('imagen/icono.png'))

        # Estilos CSS para la interfaz
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
            QTableWidget {
                font-size: 14px;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #0066cc;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
                       
        """)

        # Crear un contenedor principal con diseño horizontal
        contenedor_principal = QWidget()
        layout_principal = QHBoxLayout()

        # Crear la barra lateral
        barra_lateral = QVBoxLayout()

        imagen_label = QLabel(self)
        pixmap = QPixmap('imagen/imagen.jpg').scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imagen_label.setPixmap(pixmap)
        imagen_label.setAlignment(Qt.AlignCenter)
        barra_lateral.addWidget(imagen_label)

        # Botones de la barra lateral
        btn_registrar_transaccion = QPushButton("Registrar Transacción", self)
        btn_registrar_transaccion.clicked.connect(self.abrir_formulario_transaccion)
        barra_lateral.addWidget(btn_registrar_transaccion)

        btn_ver_libro_diario = QPushButton("Ver Libro Diario", self)
        btn_ver_libro_diario.clicked.connect(self.ver_libro_diario)
        barra_lateral.addWidget(btn_ver_libro_diario)

        btn_ver_libro_mayor = QPushButton("Ver Libro Mayor", self)
        btn_ver_libro_mayor.clicked.connect(self.ver_libro_mayor)
        barra_lateral.addWidget(btn_ver_libro_mayor)

        btn_verificar_balance = QPushButton("Verificar Balance", self)
        btn_verificar_balance.clicked.connect(self.verificar_balance)
        barra_lateral.addWidget(btn_verificar_balance)

        btn_generar_pdf = QPushButton("Generar PDF", self)
        btn_generar_pdf.clicked.connect(self.abrir_ventana_generar_pdf)
        barra_lateral.addWidget(btn_generar_pdf)

        # Espaciador para empujar los botones hacia arriba
        barra_lateral.addStretch()

        # Crear un área principal con un QStackedWidget para mostrar contenido dinámico
        self.area_principal = QStackedWidget()

        # Agregar la barra lateral y el área principal al layout principal
        layout_principal.addLayout(barra_lateral, 1)  # Barra lateral ocupa 1 parte
        layout_principal.addWidget(self.area_principal, 4)  # Área principal ocupa 4 partes

        # Configurar el contenedor principal
        contenedor_principal.setLayout(layout_principal)
        self.setCentralWidget(contenedor_principal)

    def abrir_formulario_transaccion(self):
        # Limpiar el área principal eliminando widgets existentes
        while self.area_principal.count():
            widget = self.area_principal.widget(0)
            self.area_principal.removeWidget(widget)
            widget.deleteLater()

        # Crear el formulario de transacción
        formulario = QWidget()
        layout = QVBoxLayout()

        self.campos_debe = []
        self.campos_haber = []

        self.input_fecha = QDateEdit()
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

        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Descripción")
        layout.addWidget(self.input_descripcion)

        btn_guardar = QPushButton("Guardar Transacción")
        btn_guardar.clicked.connect(self.guardar_transaccion)
        layout.addWidget(btn_guardar)

        formulario.setLayout(layout)
        self.area_principal.addWidget(formulario)
        self.area_principal.setCurrentWidget(formulario)

    def agregar_campo_debe(self):
        """Agrega un campo de cuenta y monto para el Debe."""
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
        """Agrega un campo de cuenta y monto para el Haber."""
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
        """Guarda la transacción en la base de datos."""
        try:
            fecha = self.input_fecha.date().toString("yyyy-MM-dd")
            cuentas_debe = [campo[0].text() for campo in self.campos_debe if campo[0].text()]
            montos_debe = [float(campo[1].text()) for campo in self.campos_debe if campo[1].text()]
            cuentas_haber = [campo[0].text() for campo in self.campos_haber if campo[0].text()]
            montos_haber = [float(campo[1].text()) for campo in self.campos_haber if campo[1].text()]
            descripcion = self.input_descripcion.text()

            if registrar_transaccion(fecha, cuentas_debe, montos_debe, cuentas_haber, montos_haber, descripcion):
                QMessageBox.information(self, "Éxito", "Transacción registrada con éxito.")
                self.abrir_formulario_transaccion()  # Limpiar el formulario
            else:
                QMessageBox.warning(self, "Error", "Los montos de Debe y Haber no coinciden.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Debe ingresar valores numéricos válidos.")

    def ver_libro_diario(self):
        # Limpiar el área principal eliminando widgets existentes
        while self.area_principal.count():
            widget = self.area_principal.widget(0)
            self.area_principal.removeWidget(widget)
            widget.deleteLater()

        # Obtener el libro diario
        libro_diario = obtener_libro_diario()

        # Crear la tabla para mostrar el libro diario
        tabla = QTableWidget()
        tabla.setColumnCount(5)  # Fecha, Concepto, Debe, Haber, Descripción
        tabla.setHorizontalHeaderLabels(["Fecha", "Concepto", "Debe", "Haber", "Descripción"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Estilos para la tabla (manteniendo el estilo anterior)
        tabla.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #0066cc;  /* Azul */
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # Llenar la tabla con los datos del libro diario
        for transaccion in libro_diario:
            fecha = transaccion["fecha"]
            descripcion = transaccion["descripcion"]
            cuentas_debe = transaccion["cuentas_debe"]
            montos_debe = transaccion["montos_debe"]
            cuentas_haber = transaccion["cuentas_haber"]
            montos_haber = transaccion["montos_haber"]

            # Agregar filas para las cuentas Debe
            for cuenta, monto in zip(cuentas_debe, montos_debe):
                fila = tabla.rowCount()
                tabla.insertRow(fila)
                tabla.setItem(fila, 0, QTableWidgetItem(fecha))
                tabla.setItem(fila, 1, QTableWidgetItem(cuenta))
                tabla.setItem(fila, 2, QTableWidgetItem(f"{monto:.2f}"))
                tabla.setItem(fila, 3, QTableWidgetItem(""))  # Haber en blanco
                tabla.setItem(fila, 4, QTableWidgetItem(descripcion))

            # Agregar filas para las cuentas Haber
            for cuenta, monto in zip(cuentas_haber, montos_haber):
                fila = tabla.rowCount()
                tabla.insertRow(fila)
                tabla.setItem(fila, 0, QTableWidgetItem(fecha))
                tabla.setItem(fila, 1, QTableWidgetItem(cuenta))
                tabla.setItem(fila, 2, QTableWidgetItem(""))  # Debe en blanco
                tabla.setItem(fila, 3, QTableWidgetItem(f"{monto:.2f}"))
                tabla.setItem(fila, 4, QTableWidgetItem(descripcion))

        # Ajustar el tamaño de las filas y columnas
        tabla.resizeRowsToContents()
        tabla.resizeColumnsToContents()

        # Agregar la tabla al área principal
        self.area_principal.addWidget(tabla)
        self.area_principal.setCurrentWidget(tabla)

    def ver_libro_mayor(self):
        # Limpiar el área principal eliminando widgets existentes
        while self.area_principal.count():
            widget = self.area_principal.widget(0)
            self.area_principal.removeWidget(widget)
            widget.deleteLater()

        # Obtener el libro mayor
        libro_mayor = obtener_libro_mayor()

        # Crear la tabla para mostrar el libro mayor
        tabla = QTableWidget()
        tabla.setColumnCount(2)  # Cuenta, Saldo
        tabla.setHorizontalHeaderLabels(["Cuenta", "Saldo"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Llenar la tabla con los datos del libro mayor
        tabla.setRowCount(len(libro_mayor))
        for i, cuenta in enumerate(libro_mayor):
            tabla.setItem(i, 0, QTableWidgetItem(cuenta["cuenta"]))
            tabla.setItem(i, 1, QTableWidgetItem(str(cuenta["saldo"])))

        # Agregar la tabla al área principal
        self.area_principal.addWidget(tabla)
        self.area_principal.setCurrentWidget(tabla)

    def verificar_balance(self):
        # Limpiar el área principal eliminando widgets existentes
        while self.area_principal.count():
            widget = self.area_principal.widget(0)
            self.area_principal.removeWidget(widget)
            widget.deleteLater()

        # Mostrar el balance en el área principal
        balance = verificar_balance()
        texto = (
            f"Total Debe: {balance['total_debe']}\n"
            f"Total Haber: {balance['total_haber']}\n\n"
        )
        texto += "El balance está equilibrado." if balance["equilibrado"] else "El balance no está equilibrado."

        etiqueta = QLabel(texto)
        etiqueta.setWordWrap(True)
        self.area_principal.addWidget(etiqueta)
        self.area_principal.setCurrentWidget(etiqueta)
 

    def abrir_ventana_generar_pdf(self):
        """
        Abre una ventana emergente con dos opciones: PDF Libro Mayor y PDF Libro Diario.
        """
        ventana_opciones = QDialog(self)
        ventana_opciones.setWindowTitle("Generar PDF")
        layout_opciones = QVBoxLayout()

        # Botón para generar PDF del Libro Mayor
        btn_pdf_libro_mayor = QPushButton("PDF Libro Mayor", ventana_opciones)
        btn_pdf_libro_mayor.clicked.connect(lambda: self.generar_pdf_libro_mayor(ventana_opciones))
        layout_opciones.addWidget(btn_pdf_libro_mayor)

        # Botón para generar PDF del Libro Diario
        btn_pdf_libro_diario = QPushButton("PDF Libro Diario", ventana_opciones)
        btn_pdf_libro_diario.clicked.connect(lambda: self.generar_pdf_libro_diario(ventana_opciones))
        layout_opciones.addWidget(btn_pdf_libro_diario)

        ventana_opciones.setLayout(layout_opciones)
        ventana_opciones.exec_()

    def generar_pdf_libro_mayor(self, ventana_opciones):
        """
        Genera el PDF del libro mayor.
        """
        ventana_opciones.close()  # Cerrar la ventana de opciones

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

        # Obtener la fecha de emisión
        fecha_emision = QDate.currentDate().toString("yyyy-MM-dd")

        # Obtener el libro mayor
        libro_mayor = obtener_libro_mayor()

        try:
            pdf_path = generar_pdf_libro_mayor(nombre_empresa, libro_mayor, tasa_dolar, fecha_emision)
            QMessageBox.information(self, "Éxito", f"PDF generado correctamente: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {str(e)}")

    def generar_pdf_libro_diario(self, ventana_opciones):
        """
        Genera el PDF del libro diario.
        """
        ventana_opciones.close()  # Cerrar la ventana de opciones

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
       

def iniciar_interfaz():
    """
    Inicializa la interfaz de usuario.
    """
    inicializar_base_datos()
    app = QApplication([])
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec_()