import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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

def obtener_numero_referencia(cuenta):
    """
    Obtiene el número de referencia único para una cuenta.
    Si la cuenta no existe, se le asigna un nuevo número de referencia.
    """
    conn = sqlite3.connect(DB_PATH)
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
        conn.commit()

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

    # Guardar la transacción en la base de datos
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
        numero_referencia = obtener_numero_referencia(cuenta)
        cursor.execute("""
            INSERT INTO detalles_transacciones (transaccion_id, cuenta, monto, tipo)
            VALUES (?, ?, ?, 'Debe')
        """, (transaccion_id, cuenta, monto))

        # Actualizar libro mayor (Cuenta debe)
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
        numero_referencia = obtener_numero_referencia(cuenta)
        cursor.execute("""
            INSERT INTO detalles_transacciones (transaccion_id, cuenta, monto, tipo)
            VALUES (?, ?, ?, 'Haber')
        """, (transaccion_id, cuenta, monto))

        # Actualizar libro mayor (Cuenta haber)
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

def obtener_libro_diario():
    """
    Retorna todas las transacciones registradas en la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener transacciones principales
    cursor.execute("""
        SELECT id, fecha, descripcion FROM transacciones
    """)
    transacciones = cursor.fetchall()

    libro_diario = []
    for transaccion in transacciones:
        transaccion_id, fecha, descripcion = transaccion

        # Obtener detalles de la transacción
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

    # Calcular totales de Debe y Haber
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

def generar_pdf_libro_diario(nombre_empresa, libro_diario, tasa_dolar):
    """
    Genera un PDF con el libro diario, mostrando montos en Bs y USD.
    """
    try:
        pdf_path = "libro_diario.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"<b>Nombre de la Empresa:</b> {nombre_empresa}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Tipo de cambio:</b> 1 USD = {tasa_dolar} Bs", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Crear la tabla
        data = [["Fecha", "Operaciones", "N° Referencia", "Debe", "Haber", "Descripción"]]
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

            # Mostrar cuentas de Debe (activos) primero
            for cuenta, monto_bs in zip(cuentas_debe, montos_debe):
                monto_usd = monto_bs / tasa_dolar if tasa_dolar != 0 else 0
                data.append([
                    fecha,
                    cuenta,
                    referencias[cuenta],
                    f"Bs {monto_bs:.2f}\n(USD {monto_usd:.2f})",
                    "",
                    descripcion
                ])

            # Mostrar cuentas de Haber (pasivos) después
            for cuenta, monto_bs in zip(cuentas_haber, montos_haber):
                monto_usd = monto_bs / tasa_dolar if tasa_dolar != 0 else 0
                data.append([
                    fecha,
                    cuenta,
                    referencias[cuenta],
                    "",
                    f"Bs {monto_bs:.2f}\n(USD {monto_usd:.2f})",
                    descripcion
                ])

        table = Table(data)
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