libro_diario = []  # Lista para registrar las transacciones
cuentas = {}  # Diccionario para las cuentas T


def registrar_transaccion(fecha, cuenta_debe, monto_debe, cuenta_haber, monto_haber, descripcion):
    """
    Registra una transacción en el libro diario y actualiza las cuentas.
    """
    # Verificar que el debe y el haber sean iguales
    if monto_debe <= 0 or monto_haber <= 0:
        return False
    if monto_debe != monto_haber:
        return False

    # Agregar al libro diario
    transaccion = {
        "fecha": fecha,
        "cuenta_debe": cuenta_debe,
        "monto_debe": monto_debe,
        "cuenta_haber": cuenta_haber,
        "monto_haber": monto_haber,
        "descripcion": descripcion,
    }
    libro_diario.append(transaccion)

    # Actualizar las cuentas T
    if cuenta_debe not in cuentas:
        cuentas[cuenta_debe] = {"Debe": [], "Haber": []}
    if cuenta_haber not in cuentas:
        cuentas[cuenta_haber] = {"Debe": [], "Haber": []}

    cuentas[cuenta_debe]["Debe"].append(monto_debe)
    cuentas[cuenta_haber]["Haber"].append(monto_haber)

    return True


def obtener_libro_diario():
    """
    Retorna el libro diario con todas las transacciones registradas.
    """
    return libro_diario


def verificar_balance():
    """
    Verifica si el balance contable está equilibrado.
    """
    total_debe = sum(t["monto_debe"] for t in libro_diario)
    total_haber = sum(t["monto_haber"] for t in libro_diario)
    return {
        "total_debe": total_debe,
        "total_haber": total_haber,
        "equilibrado": total_debe == total_haber,
    }
