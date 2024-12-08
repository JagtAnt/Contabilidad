# Programa de contabilidad: Libro Diario y Cuentas T

# Estructuras para almacenar datos
libro_diario = []  # Lista para registrar las transacciones
cuentas = {}  # Diccionario para las cuentas T


# Función para registrar una transacción
def registrar_transaccion():
    print("\n--- Registrar Transacción ---")
    fecha = input("Fecha (YYYY-MM-DD): ")
    cuenta_debe = input("Cuenta (Debe): ")
    cuenta_haber = input("Cuenta (Haber): ")
    try:
        monto_debe = float(input("Monto (Debe): "))
        monto_haber = float(input("Monto (Haber): "))
    except ValueError:
        print("Error: Debe ingresar un valor numérico.")
        return

    cuenta_haber = input("Cuenta (Haber): ")
    descripcion = input("Descripción: ")

    # Verificar que el débito y el crédito sean iguales
    if monto_debe <= 0 or monto_haber <= 0:
        print("Error: Los montos de Debe y Haber deben ser positivos.")
        return
    if monto_debe != monto_haber:
        print("Error: El monto del Débito y el Crédito deben ser iguales.")
        return

    # Agregar al libro diario
    transaccion = {
        "fecha": fecha,
        "cuenta_debe": cuenta_debe,
        "monto_debe": monto_debe,
        "cuenta_haber": cuenta_haber,
        "monto_haber": monto_haber,
        "descripcion": descripcion
    }
    libro_diario.append(transaccion)

    # Actualizar las cuentas T
    if cuenta_debe not in cuentas:
        cuentas[cuenta_debe] = {"Debe": [], "Haber": []}
    if cuenta_haber not in cuentas:
        cuentas[cuenta_haber] = {"Debe": [], "Haber": []}

    cuentas[cuenta_debe]["Debe"].append(monto_debe)
    cuentas[cuenta_haber]["Haber"].append(monto_haber)

    print("Transacción registrada con éxito.")


# Función para mostrar el libro diario
def mostrar_libro_diario():
    print("\n--- Libro Diario ---")
    if not libro_diario:
        print("No hay transacciones registradas.")
        return
    for t in libro_diario:
        print(f"{t['fecha']} | Debe: {t['cuenta_debe']} ({t['monto_debe']}) | "
              f"Haber: {t['cuenta_haber']} ({t['monto_haber']}) | {t['descripcion']}")


# Función para mostrar las cuentas T
def mostrar_cuentas_t():
    print("\n--- Cuentas T ---")
    if not cuentas:
        print("No hay cuentas registradas.")
        return
    for cuenta, movimientos in cuentas.items():
        print(f"\nCuenta: {cuenta}")
        print("Debe: ", movimientos["Debe"])
        print("Haber:", movimientos["Haber"])


# Función para verificar el balance
def verificar_balance():
    total_debe = sum(t["monto_debe"] for t in libro_diario)
    total_haber = sum(t["monto_haber"] for t in libro_diario)
    print("\n--- Verificación Contable ---")
    print(f"Total Debe: {total_debe}")
    print(f"Total Haber: {total_haber}")
    if total_debe == total_haber:
        print("La contabilidad está equilibrada.")
    else:
        print("Error: El Debe y el Haber no coinciden.")


# Menú principal
def menu():
    while True:
        print("\n--- Menú Principal ---")
        print("1. Registrar Transacción")
        print("2. Mostrar Libro Diario")
        print("3. Mostrar Cuentas T")
        print("4. Verificar Balance")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_transaccion()
        elif opcion == "2":
            mostrar_libro_diario()
        elif opcion == "3":
            mostrar_cuentas_t()
        elif opcion == "4":
            verificar_balance()
        elif opcion == "5":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

# Inicia el programa
menu()