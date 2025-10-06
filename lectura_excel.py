import pandas as pd
import random
import time
import serial
import serial.tools.list_ports

# --- CONFIGURACIÓN DE RANGOS ---
RANGOS = {
    "temp": (0, 50),
    "tds": (0, 100),
    "ec": (-250, 250),
    "orp": (-50, 1000),
    "sal": (0, 56),
    "do": (0, 56),
    "turb": (0, 56),
    "ph": (0, 56),
}

# --- CONFIGURACIÓN DE PUERTOS SERIAL ---
ESP32_PORTS = {
    "verso1": "/dev/ttyUSB0",
    "verso2": "/dev/ttyUSB1",
    "verso3": "/dev/ttyUSB2"
}

SERIAL_CONFIG = {
    'baudrate': 9600,
    'timeout': 1
}


def detectar_puertos_seriales():
    puertos = [port.device for port in serial.tools.list_ports.comports()]
    print("Puertos seriales detectados:", puertos)
    return puertos


def inicializar_conexiones_seriales():
    conexiones = {}
    for nombre, puerto in ESP32_PORTS.items():
        try:
            conexiones[nombre] = serial.Serial(puerto, **SERIAL_CONFIG)
            time.sleep(2)
            print(f"Conexión establecida con {nombre} en {puerto}")
        except Exception as e:
            print(f"Error conectando a {nombre} en {puerto}: {e}")
            conexiones[nombre] = None
    return conexiones


def enviar_verso(conexion, verso):
    if conexion and conexion.is_open:
        try:
            mensaje = f"{verso}\n"
            conexion.write(mensaje.encode('utf-8'))
            print(f"Enviado: {verso}")
            return True
        except Exception as e:
            print(f"Error enviando verso: {e}")
    else:
        print("Conexión serial no disponible")
    return False


def leer_datos_sensores(archivo_csv):
    return pd.read_csv(archivo_csv)


def leer_haikus(archivo_excel):
    df = pd.read_excel(archivo_excel)
    df.columns = df.columns.str.strip()
    return df


def seleccionar_verso(columna, valor_sensor, df_haikus):
    minimo, maximo = RANGOS.get(columna, (0, len(df_haikus) - 1))
    idx_inicial = int((valor_sensor % (maximo - minimo + 1)) + minimo)
    idx_final = min(idx_inicial + 10, maximo)
    fila = random.randint(idx_inicial, idx_final)
    return df_haikus.iloc[fila][columna]


def generar_haiku(df_sensores, df_haikus):
    ultima_fila = df_sensores.iloc[-1]
    verso1 = seleccionar_verso("Verso 1 (5 sílabas)", ultima_fila["temp"], df_haikus)
    verso2 = seleccionar_verso("Verso 2 (7 sílabas)", ultima_fila["tds"], df_haikus)
    verso3 = seleccionar_verso("Verso 3 (5 sílabas)", ultima_fila["ph"], df_haikus)
    return verso1, verso2, verso3


def main():
    archivo_csv = "aquarium_readings.csv"
    archivo_excel = "Hidropoeticas_Haikus.xlsx"

    detectar_puertos_seriales()
    conexiones = inicializar_conexiones_seriales()

    df_sensores = leer_datos_sensores(archivo_csv)
    df_haikus = leer_haikus(archivo_excel)

    print("\n=== INICIO DEL CICLO INFINITO DE HAIKUS ===\n")

    try:
        while True:
            v1, v2, v3 = generar_haiku(df_sensores, df_haikus)

            print(f"Verso 1: {v1}")
            print(f"Verso 2: {v2}")
            print(f"Verso 3: {v3}")

            # Enviar con pausas aleatorias entre versos
            if enviar_verso(conexiones.get("verso1"), v1):
                time.sleep(random.uniform(1.0, 4.0))

            if enviar_verso(conexiones.get("verso2"), v2):
                time.sleep(random.uniform(1.0, 4.0))

            if enviar_verso(conexiones.get("verso3"), v3):
                time.sleep(random.uniform(1.0, 4.0))

            # Esperar entre haikus un tiempo aleatorio (5–15 segundos)
            pausa = random.uniform(5.0, 15.0)
            print(f"Esperando {pausa:.1f} segundos antes del próximo haiku...\n")
            time.sleep(pausa)

    except KeyboardInterrupt:
        print("\n--- Ejecución interrumpida manualmente ---")

    finally:
        for nombre, conexion in conexiones.items():
            if conexion and conexion.is_open:
                conexion.close()
                print(f"Conexión {nombre} cerrada")
        print("Programa finalizado.")


if __name__ == "__main__":
    main()
