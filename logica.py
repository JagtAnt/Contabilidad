import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Se añade ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # Se importan ambas constantes de alineación
from datetime import datetime

DB_PATH = "contabilidad.db"

def inicializar_base_datos():
    """
    Crea las tablas necesarias si no existen.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla transacciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT
        )
    """)

    # Crear tabla detalles_transacciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalles_transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaccion_id INTEGER NOT NULL,
            cuenta TEXT NOT NULL,
            monto REAL NOT NULL,
            tipo TEXT CHECK(tipo IN ('Debe', 'Haber')) NOT NULL,
            FOREIGN KEY (transaccion_id) REFERENCES transacciones(id)
        )
    """)

    # Crear tabla referencias_cuentas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referencias_cuentas (
            cuenta TEXT PRIMARY KEY,
            numero_referencia INTEGER NOT NULL
        )
    """)

    # Crear tabla para el libro mayor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libro_mayor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cuenta TEXT UNIQUE NOT NULL,
            saldo REAL NOT NULL DEFAULT 0,
            fecha TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def obtener_numero_referencia(cuenta, conn=None):
    """
    Obtiene el número de referencia único para una cuenta.
    Si la cuenta no existe, se le asigna un nuevo número de referencia.
    """
    cerrar_conexion = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        cerrar_conexion = True

    cursor = conn.cursor()

    # Verificar si la cuenta ya tiene un número de referencia
    cursor.execute("""
        SELECT numero_referencia FROM referencias_cuentas WHERE cuenta = ?
    """, (cuenta,))
    resultado = cursor.fetchone()

    if resultado:
        numero_referencia = resultado[0]
    else:
        # Obtener el último número de referencia asignado
        cursor.execute("""
            SELECT MAX(numero_referencia) FROM referencias_cuentas
        """)
        ultimo_numero = cursor.fetchone()[0] or 0
        numero_referencia = ultimo_numero + 1

        # Asignar el nuevo número de referencia a la cuenta
        cursor.execute("""
            INSERT INTO referencias_cuentas (cuenta, numero_referencia)
            VALUES (?, ?)
        """, (cuenta, numero_referencia))
        if cerrar_conexion:
            conn.commit()

    if cerrar_conexion:
        conn.close()

    return numero_referencia


def registrar_transaccion(fecha, cuentas_debe, montos_debe, cuentas_haber, montos_haber, descripcion):
    """
    Registra una transacción en la base de datos y actualiza el libro mayor.
    """
    if not cuentas_debe or not cuentas_haber or not montos_debe or not montos_haber:
        return False

    total_debe = sum(montos_debe)
    total_haber = sum(montos_haber)

    # Verificar que los totales sean iguales
    if total_debe != total_haber:
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insertar en transacciones
    cursor.execute("""
        INSERT INTO transacciones (fecha, descripcion)
        VALUES (?, ?)
    """, (fecha, descripcion))
    transaccion_id = cursor.lastrowid

    # Insertar detalles de la transacción (Debe)
    for cuenta, monto in zip(cuentas_debe, montos_debe):
        numero_referencia = obtener_numero_referencia(cuenta, conn)
        cursor.execute("""
            INSERT INTO detalles_transacciones (transaccion_id, cuenta, monto, tipo)
            VALUES (?, ?, ?, 'Debe')
        """, (transaccion_id, cuenta, monto))

        # Actualizar libro mayor (Cuenta Debe)
        cursor.execute("""
            SELECT saldo FROM libro_mayor WHERE cuenta = ?
        """, (cuenta,))
        resultado = cursor.fetchone()

        if resultado:
            saldo_actual = resultado[0]
            nuevo_saldo = saldo_actual + monto
            cursor.execute("""
                UPDATE libro_mayor SET saldo = ? WHERE cuenta = ?
            """, (nuevo_saldo, cuenta))
        else:
            cursor.execute("""
                INSERT INTO libro_mayor (cuenta, saldo, fecha)
                VALUES (?, ?, ?)
            """, (cuenta, monto, fecha))

    # Insertar detalles de la transacción (Haber)
    for cuenta, monto in zip(cuentas_haber, montos_haber):
        numero_referencia = obtener_numero_referencia(cuenta, conn)
        cursor.execute("""
            INSERT INTO detalles_transacciones (transaccion_id, cuenta, monto, tipo)
            VALUES (?, ?, ?, 'Haber')
        """, (transaccion_id, cuenta, monto))

        # Actualizar libro mayor (Cuenta Haber)
        cursor.execute("""
            SELECT saldo FROM libro_mayor WHERE cuenta = ?
        """, (cuenta,))
        resultado = cursor.fetchone()

        if resultado:
            saldo_actual = resultado[0]
            nuevo_saldo = saldo_actual - monto
            cursor.execute("""
                UPDATE libro_mayor SET saldo = ? WHERE cuenta = ?
            """, (nuevo_saldo, cuenta))
        else:
            cursor.execute("""
                INSERT INTO libro_mayor (cuenta, saldo, fecha)
                VALUES (?, ?, ?)
            """, (cuenta, -monto, fecha))

    conn.commit()
    conn.close()
    return True


def obtener_libro_diario(fecha_inicio=None, fecha_fin=None):
    """
    Retorna todas las transacciones registradas en la base de datos dentro de un rango de fechas.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT id, fecha, descripcion FROM transacciones
    """
    params = []

    if fecha_inicio and fecha_fin:
        query += " WHERE fecha BETWEEN ? AND ?"
        params.extend([fecha_inicio, fecha_fin])
    elif fecha_inicio:
        query += " WHERE fecha >= ?"
        params.append(fecha_inicio)
    elif fecha_fin:
        query += " WHERE fecha <= ?"
        params.append(fecha_fin)

    cursor.execute(query, params)
    transacciones = cursor.fetchall()

    libro_diario = []
    for transaccion in transacciones:
        transaccion_id, fecha, descripcion = transaccion

        cursor.execute("""
            SELECT cuenta, monto, tipo FROM detalles_transacciones
            WHERE transaccion_id = ?
        """, (transaccion_id,))
        detalles = cursor.fetchall()

        cuentas_debe = [d[0] for d in detalles if d[2] == 'Debe']
        montos_debe = [d[1] for d in detalles if d[2] == 'Debe']
        cuentas_haber = [d[0] for d in detalles if d[2] == 'Haber']
        montos_haber = [d[1] for d in detalles if d[2] == 'Haber']

        libro_diario.append({
            "fecha": fecha,
            "descripcion": descripcion,
            "cuentas_debe": cuentas_debe,
            "montos_debe": montos_debe,
            "cuentas_haber": cuentas_haber,
            "montos_haber": montos_haber,
        })

    conn.close()
    return libro_diario


def verificar_balance():
    """
    Verifica si el libro diario está equilibrado.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(monto) FROM detalles_transacciones WHERE tipo = 'Debe'
    """)
    total_debe = cursor.fetchone()[0] or 0.0

    cursor.execute("""
        SELECT SUM(monto) FROM detalles_transacciones WHERE tipo = 'Haber'
    """)
    total_haber = cursor.fetchone()[0] or 0.0

    conn.close()
    return {
        "total_debe": total_debe,
        "total_haber": total_haber,
        "equilibrado": total_debe == total_haber,
    }


def obtener_libro_mayor():
    """
    Obtiene las cuentas y los saldos registrados en el libro mayor desde la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cuenta, saldo FROM libro_mayor
    """)
    cuentas = cursor.fetchall()

    conn.close()
    return [{'cuenta': cuenta, 'saldo': saldo} for cuenta, saldo in cuentas]


def generar_pdf_libro_diario(nombre_empresa, libro_diario, tasa_dolar, fecha_inicio, fecha_fin):
    """
    Genera un PDF con el libro diario, mostrando montos en Bs y USD,
    e incluye en el encabezado: nombre de empresa, tipo de cambio,
    período de fechas y la fecha de emisión.
    """
    try:
        pdf_path = "libro_diario.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []

        # Estilos base
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle("header_style",
                                      parent=styles["Normal"],
                                      alignment=TA_LEFT)

        # Obtener la fecha y hora de emisión
        fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Construir el encabezado
        header_text = (
            f"<b>Nombre de la Empresa:</b> {nombre_empresa}<br/>"
            f"<b>Tipo de cambio:</b> 1 USD = {tasa_dolar} Bs<br/>"
            f"<b>Periodo:</b> {fecha_inicio} a {fecha_fin}<br/>"
            f"<b>Fecha de emisión:</b> {fecha_emision}"
        )
        elements.append(Paragraph(header_text, header_style))
        elements.append(Spacer(1, 12))

        # Estilo para la descripción (dentro de la tabla)
        style_desc = styles["Normal"]
        style_desc.alignment = TA_CENTER
        style_desc.wordWrap = 'CJK'

        # Creación de la tabla (cuadro)
        data = [["Fecha", "Operaciones", "N° Ref", "Debe", "Haber", "Descripción"]]
        for transaccion in libro_diario:
            fecha = transaccion["fecha"]
            descripcion = transaccion["descripcion"]
            cuentas_debe = transaccion["cuentas_debe"]
            montos_debe = transaccion["montos_debe"]
            cuentas_haber = transaccion["cuentas_haber"]
            montos_haber = transaccion["montos_haber"]

            # Obtener números de referencia para las cuentas
            referencias = {}
            for cuenta in cuentas_debe + cuentas_haber:
                referencias[cuenta] = obtener_numero_referencia(cuenta)

            # Calcular total de operaciones (para uso en el estilo de la tabla)
            total_operaciones = len(cuentas_debe) + len(cuentas_haber)

            # Agregar filas para las cuentas Debe
            for i, (cuenta, monto_bs) in enumerate(zip(cuentas_debe, montos_debe)):
                monto_usd = monto_bs / tasa_dolar if tasa_dolar != 0 else 0
                if i == 0:
                    data.append([
                        fecha,
                        cuenta,
                        referencias[cuenta],
                        f"Bs {monto_bs:.2f}\n(USD {monto_usd:.2f})",
                        "",
                        Paragraph(descripcion, style_desc)
                    ])
                else:
                    data.append([
                        "",
                        cuenta,
                        referencias[cuenta],
                        f"Bs {monto_bs:.2f}\n(USD {monto_usd:.2f})",
                        "",
                        ""
                    ])

            # Agregar filas para las cuentas Haber
            for i, (cuenta, monto_bs) in enumerate(zip(cuentas_haber, montos_haber)):
                monto_usd = monto_bs / tasa_dolar if tasa_dolar != 0 else 0
                if i == 0 and not cuentas_debe:
                    data.append([
                        fecha,
                        cuenta,
                        referencias[cuenta],
                        "",
                        f"Bs {monto_bs:.2f}\n(USD {monto_usd:.2f})",
                        Paragraph(descripcion, style_desc)
                    ])
                else:
                    data.append([
                        "",
                        cuenta,
                        referencias[cuenta],
                        "",
                        f"Bs {monto_bs:.2f}\n(USD {monto_usd:.2f})",
                        ""
                    ])

        # Crear la tabla con anchos personalizados
        table = Table(data, colWidths=[60, 100, 60, 80, 80, 200])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (5, 0), (5, -1), "CENTER"),
            ("VALIGN", (5, 1), (5, -1), "MIDDLE"),
            ("SPAN", (5, 1), (5, total_operaciones)),
        ]))
        elements.append(table)
        doc.build(elements)

        return pdf_path
    except Exception as e:
        raise Exception(f"No se pudo generar el PDF: {str(e)}")
    
def generar_pdf_libro_mayor(nombre_empresa, libro_mayor, tasa_dolar, fecha_emision):
    """
    Genera un PDF del Libro Mayor mostrando los movimientos de cada cuenta en una tabla con las columnas:
      Fecha | Concepto | N° Ref | Debe | Haber | Saldo
    Los movimientos se ordenan cronológicamente y se calcula el saldo acumulado.
    """
    try:
        pdf_path = "libro_mayor.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle("header_style", parent=styles["Normal"], alignment=TA_LEFT)
        table_header_style = ParagraphStyle("table_header_style", parent=styles["Normal"],
                                            alignment=TA_CENTER, fontName="Helvetica-Bold")
        # Estilo para el contenido de la columna "Concepto" con ajuste de línea
        concept_style = ParagraphStyle("concept_style", parent=styles["Normal"],
                                       alignment=TA_LEFT, wordWrap='CJK')
        
        # Fecha y encabezado principal
        fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_text = (
            f"<b>Nombre de la Empresa:</b> {nombre_empresa}<br/>"
            f"<b>Tipo de Cambio:</b> 1 USD = {tasa_dolar} Bs<br/>"
            f"<b>Fecha de Emisión:</b> {fecha_emision}<br/>"
            f"<b>Libro Mayor - Movimientos</b>"
        )
        elements.append(Paragraph(header_text, header_style))
        elements.append(Spacer(1, 12))
        
        # Conexión a la base de datos y obtención de las cuentas en el libro mayor
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT cuenta, saldo FROM libro_mayor")
        cuentas = cursor.fetchall()
        
        # Para cada cuenta se generan los movimientos en una tabla ordenada por fecha
        for cuenta, saldo in cuentas:
            # Agregar un encabezado para la cuenta
            elements.append(Paragraph(f"<b>Cuenta: {cuenta}</b>", header_style))
            elements.append(Spacer(1, 6))
            
            # Cabecera de la tabla: Fecha, Concepto, N° Ref, Debe, Haber, Saldo
            data = []
            data.append([
                Paragraph("<b>Fecha</b>", table_header_style),
                Paragraph("<b>Concepto</b>", table_header_style),
                Paragraph("<b>N° Ref</b>", table_header_style),
                Paragraph("<b>Debe</b>", table_header_style),
                Paragraph("<b>Haber</b>", table_header_style),
                Paragraph("<b>Saldo</b>", table_header_style)
            ])
            
            # Consultar los movimientos para la cuenta (unir con transacciones para obtener fecha y descripción)
            cursor.execute("""
                SELECT t.fecha, t.descripcion, dt.monto, dt.tipo
                FROM detalles_transacciones dt
                JOIN transacciones t ON dt.transaccion_id = t.id
                WHERE dt.cuenta = ?
                ORDER BY t.fecha, dt.id
            """, (cuenta,))
            movimientos = cursor.fetchall()
            
            running_balance = 0.0
            ref = obtener_numero_referencia(cuenta)  # Número de referencia de la cuenta
            
            # Recorrer cada movimiento y calcular el saldo acumulado
            for mov in movimientos:
                fecha_mov, concepto, monto, tipo = mov
                if tipo == "Debe":
                    debe = monto
                    haber = ""
                    running_balance += monto
                else:
                    debe = ""
                    haber = monto
                    running_balance -= monto
                
                debe_str = f"Bs {debe:.2f}" if debe != "" else ""
                haber_str = f"Bs {haber:.2f}" if haber != "" else ""
                saldo_str = f"Bs {running_balance:.2f}"
                
                data.append([
                    Paragraph(fecha_mov, styles["Normal"]),
                    Paragraph(concepto, concept_style),
                    Paragraph(str(ref), styles["Normal"]),
                    Paragraph(debe_str, styles["Normal"]),
                    Paragraph(haber_str, styles["Normal"]),
                    Paragraph(saldo_str, styles["Normal"])
                ])
            
            # Crear la tabla con anchos fijos para cada columna
            table_mov = Table(data, colWidths=[70, 150, 50, 70, 70, 70])
            table_mov.setStyle(TableStyle([
                ("BOX", (0,0), (-1,-1), 1, colors.black),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ]))
            elements.append(table_mov)
            elements.append(Spacer(1, 24))
        
        conn.close()
        doc.build(elements)
        return pdf_path
    except Exception as e:
        raise Exception(f"No se pudo generar el PDF del Libro Mayor: {str(e)}")

def obtener_balance_sumasy_saldos():
    """
    Obtiene el balance de sumas y saldos por cuenta, calculando:
      - Total en Debe
      - Total en Haber
      - Saldo Deudor (si Debe > Haber)
      - Saldo Acreedor (si Haber > Debe)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cuenta,
               SUM(CASE WHEN tipo = 'Debe' THEN monto ELSE 0 END) AS total_debe,
               SUM(CASE WHEN tipo = 'Haber' THEN monto ELSE 0 END) AS total_haber
        FROM detalles_transacciones
        GROUP BY cuenta
    """)
    resultados = cursor.fetchall()
    conn.close()

    balances = []
    for cuenta, total_debe, total_haber in resultados:
        saldo_deudor = total_debe - total_haber if total_debe > total_haber else 0
        saldo_acreedor = total_haber - total_debe if total_haber > total_debe else 0
        balances.append({
            "cuenta": cuenta,
            "debe": total_debe,
            "haber": total_haber,
            "saldo_deudor": saldo_deudor,
            "saldo_acreedor": saldo_acreedor
        })
    return balances


def generar_pdf_balance_sumasy_saldos(nombre_empresa, tasa_dolar, fecha_inicio, fecha_fin):
    """
    Genera un PDF con el balance de sumas y saldos, mostrando montos en Bs y USD.
    Incluye en el encabezado: nombre de la empresa, tipo de cambio, período y fecha de emisión.
    
    La tabla resultante contiene las siguientes columnas:
      - Cuenta
      - Debe (Bs)
      - Haber (Bs)
      - Saldo Deudor (Bs)
      - Saldo Acreedor (Bs)
    """
    try:
        pdf_path = "balance_sumasy_saldos.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []

        # Estilos base
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle("header_style", parent=styles["Normal"], alignment=TA_LEFT)

        # Obtener la fecha y hora de emisión
        fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Construir el encabezado
        header_text = (
            f"<b>Nombre de la Empresa:</b> {nombre_empresa}<br/>"
            f"<b>Tipo de cambio:</b> 1 USD = {tasa_dolar} Bs<br/>"
            f"<b>Periodo:</b> {fecha_inicio} a {fecha_fin}<br/>"
            f"<b>Fecha de emisión:</b> {fecha_emision}"
        )
        elements.append(Paragraph(header_text, header_style))
        elements.append(Spacer(1, 12))

        # Obtener el balance de sumas y saldos
        balances = obtener_balance_sumasy_saldos()

        # Preparar los datos para la tabla
        data = [["Cuenta", "Debe (Bs)", "Haber (Bs)", "Saldo Deudor (Bs)", "Saldo Acreedor (Bs)"]]
        for registro in balances:
            data.append([
                registro["cuenta"],
                f"Bs {registro['debe']:.2f}",
                f"Bs {registro['haber']:.2f}",
                f"Bs {registro['saldo_deudor']:.2f}" if registro["saldo_deudor"] > 0 else "-",
                f"Bs {registro['saldo_acreedor']:.2f}" if registro["saldo_acreedor"] > 0 else "-"
            ])
        total_debe = sum(registro["debe"] for registro in balances)
        total_haber = sum(registro["haber"] for registro in balances)
        total_saldo_deudor = sum(registro["saldo_deudor"] for registro in balances)
        total_saldo_acreedor = sum(registro["saldo_acreedor"] for registro in balances)

        data.append([
            "Total",
            f"Bs {total_debe:.2f}",
            f"Bs {total_haber:.2f}",
            f"Bs {total_saldo_deudor:.2f}" if total_saldo_deudor > 0 else "-",
            f"Bs {total_saldo_acreedor:.2f}" if total_saldo_acreedor > 0 else "-"
        ])
        # Crear la tabla con anchos personalizados
        table = Table(data, colWidths=[200, 80, 80, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        doc.build(elements)
        return pdf_path
    except Exception as e:
        raise Exception(f"No se pudo generar el PDF: {str(e)}")
