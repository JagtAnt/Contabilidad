libro_diario = []  # Lista para registrar las transacciones

def registrar_transaccion(fecha, cuentas_debe, montos_debe, cuentas_haber, montos_haber, descripcion):
    """
    Registra una transacción con múltiples operaciones en el Debe y el Haber.
    """
    if not cuentas_debe or not cuentas_haber or not montos_debe or not montos_haber:
        return False

    total_debe = sum(montos_debe)
    total_haber = sum(montos_haber)

    # Verificar que los totales sean iguales
    if total_debe != total_haber:
        return False

    # Registrar la transacción
    transaccion = {
        "fecha": fecha,
        "cuentas_debe": cuentas_debe,
        "montos_debe": montos_debe,
        "cuentas_haber": cuentas_haber,
        "montos_haber": montos_haber,
        "descripcion": descripcion,
    }
    libro_diario.append(transaccion)
    return True

def obtener_libro_diario():
    """
    Retorna el libro diario completo.
    """
    return libro_diario

def verificar_balance():
    """
    Verifica si el libro diario está equilibrado.
    """
    total_debe = sum(sum(t["montos_debe"]) for t in libro_diario)
    total_haber = sum(sum(t["montos_haber"]) for t in libro_diario)
    return {
        "total_debe": total_debe,
        "total_haber": total_haber,
        "equilibrado": total_debe == total_haber,
    }
