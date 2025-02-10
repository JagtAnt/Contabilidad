import sqlite3

DB_PATH = "contabilidad.db"

def inicializar_base_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT
        )
    """)

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
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    inicializar_base_datos()

