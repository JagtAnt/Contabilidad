import sqlite3

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

    conn.commit()
    conn.close()

def registrar_transaccion(fecha, cuentas_debe, montos_debe, cuentas_haber, montos_haber, descripcion):
    """
    Registra una transacción en la base de datos.
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
        cursor.execute("""
            INSERT INTO detalles_transacciones (transaccion_id, cuenta, monto, tipo)
            VALUES (?, ?, ?, 'Debe')
        """, (transaccion_id, cuenta, monto))

    # Insertar detalles de la transacción (Haber)
    for cuenta, monto in zip(cuentas_haber, montos_haber):
        cursor.execute("""
            INSERT INTO detalles_transacciones (transaccion_id, cuenta, monto, tipo)
            VALUES (?, ?, ?, 'Haber')
        """, (transaccion_id, cuenta, monto))

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
