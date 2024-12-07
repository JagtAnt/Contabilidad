# Programa de contabilidad: Libro Diario y Cuentas T

# Estructuras para almacenar datos
libro_diario = []  # Lista para registrar las transacciones
cuentas = {}  # Diccionario para las cuentas T


# Función para registrar una transacción
def registrar_transaccion():
    print("\n--- Registrar Transacción ---")
    fecha = input("Fecha (YYYY-MM-DD): ")
    cuenta_debito = input("Cuenta (Débito): ")
    monto_debito = float(input("Monto (Débito): "))
    cuenta_credito = input("Cuenta (Crédito): ")
    monto_credito = float(input("Monto (Crédito): "))
    descripcion = input("Descripción: ")

    # Verificar que el débito y el crédito sean iguales
    if monto_debito != monto_credito:
        print("Error: El monto del débito y del crédito deben ser iguales.")
        return

    # Agregar al libro diario
    transaccion = {
        "fecha": fecha,
        "cuenta_debito": cuenta_debito,
        "monto_debito": monto_debito,
        "cuenta_credito": cuenta_credito,
        "monto_credito": monto_credito,
        "descripcion": descripcion
    }
    libro_diario.append(transaccion)

    # Actualizar las cuentas T
    if cuenta_debito not in cuentas:
        cuentas[cuenta_debito] = {"debitos": [], "creditos": []}
    if cuenta_credito not in cuentas:
        cuentas[cuenta_credito] = {"debitos": [], "creditos": []}

    cuentas[cuenta_debito]["debitos"].append(monto_debito)
    cuentas[cuenta_credito]["creditos"].append(monto_credito)

    print("Transacción registrada con éxito.")


# Función para mostrar el libro diario
def mostrar_libro_diario():
    print("\n--- Libro Diario ---")
    if not libro_diario:
        print("No hay transacciones registradas.")
        return
    for t in libro_diario:
        print(f"{t['fecha']} | Débito: {t['cuenta_debito']} ({t['monto_debito']}) | "
              f"Crédito: {t['cuenta_credito']} ({t['monto_credito']}) | {t['descripcion']}")


# Función para mostrar las cuentas T
def mostrar_cuentas_t():
    print("\n--- Cuentas T ---")
    if not cuentas:
        print("No hay cuentas registradas.")
        return
    for cuenta, movimientos in cuentas.items():
        print(f"\nCuenta: {cuenta}")
        print("Débitos: ", movimientos["debitos"])
        print("Créditos:", movimientos["creditos"])


# Función para verificar el balance
def verificar_balance():
    total_debitos = sum(t["monto_debito"] for t in libro_diario)
    total_creditos = sum(t["monto_credito"] for t in libro_diario)
    print("\n--- Verificación Contable ---")
    print(f"Total Débitos: {total_debitos}")
    print(f"Total Créditos: {total_creditos}")
    if total_debitos == total_creditos:
        print("La contabilidad está equilibrada.")
    else:
        print("Error: Los débitos y los créditos no coinciden.")


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