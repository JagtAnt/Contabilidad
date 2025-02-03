from interfaz import iniciar_interfaz
from logica import inicializar_base_datos

if __name__ == "__main__":
    inicializar_base_datos()  # Se asegura de que la base de datos esté configurada.
    iniciar_interfaz()