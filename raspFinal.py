import pandas as pd
import random
import time
import socket

# --- CONFIGURACIÓN TCP DE CADA ESP32 ---
ESP32_IPS = {
    "verso1": "192.168.50.29",   # Pantalla 1
    "verso2": "192.168.50.252",  # Pantalla 2
    "verso3": "192.168.50.19",   # Pantalla 3
}
ESP32_PORT = 5000

# --- PARÁMETROS DE SCROLL ---
PIXELS_POR_CARACTER = 6
SCROLL_SPEED = 50
PANEL_WIDTH = 128
NUM_HAIKUS = 50  # número de versos por columna en el Excel

def leer_ultima_fila_sensor(archivo_csv):
    """Lee únicamente la última fila del CSV para optimizar velocidad."""
    try:
        df = pd.read_csv(archivo_csv, usecols=["temp","tds","ec","orp","sal","do","turb","ph"])
        return df.iloc[-1]
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        return None

def leer_haikus(archivo_excel):
    df = pd.read_excel(archivo_excel)
    df.columns = df.columns.str.strip()
    return df

def seleccionar_verso_aleatorio(columna, valor_sensor, df_haikus):
    """
    Selecciona un verso de manera pseudo-aleatoria usando el valor del sensor
    como base y agregando un offset aleatorio para variar siempre.
    """
    base = int(valor_sensor) % NUM_HAIKUS
    offset = random.randint(0, NUM_HAIKUS - 1)
    fila = (base + offset) % NUM_HAIKUS
    return df_haikus.iloc[fila][columna]

def generar_haiku(df_haikus, ultima_fila):
    v1 = seleccionar_verso_aleatorio("Verso 1 (5 sílabas)", ultima_fila["temp"], df_haikus)
    v2 = seleccionar_verso_aleatorio("Verso 2 (7 sílabas)", ultima_fila["tds"], df_haikus)
    v3 = seleccionar_verso_aleatorio("Verso 3 (5 sílabas)", ultima_fila["ph"], df_haikus)
    return v1, v2, v3

def enviar_verso_tcp(socket_cliente, verso):
    try:
        mensaje = f"{verso}\n"
        socket_cliente.sendall(mensaje.encode('utf-8'))
        print(f"Enviado a ESP32: {verso}")
        respuesta = socket_cliente.recv(1024)
        if respuesta:
            print("Respuesta del ESP32:", respuesta.decode().strip())
        return True
    except Exception as e:
        print(f"Error enviando verso: {e}")
        return False

def calcular_tiempo_scroll(verso):
    return 10.0

def main():
    archivo_csv = "aquarium_readings.csv"
    archivo_excel = "Hidropoeticas_Haikus.xlsx"

    df_haikus = leer_haikus(archivo_excel)

    # Crear sockets persistentes para cada ESP32
    sockets = {}
    for verso, ip in ESP32_IPS.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        print(f"Conectando a {verso} en {ip}:{ESP32_PORT}...")
        s.connect((ip, ESP32_PORT))
        sockets[verso] = s
        print(f"{verso} conectado correctamente\n")

    print("=== INICIO DEL CICLO INFINITO DE HAIKUS ===\n")

    try:
        while True:
            ultima_fila = leer_ultima_fila_sensor(archivo_csv)
            if ultima_fila is None:
                time.sleep(2)
                continue

            # Mostrar valores de sensores para debug
            print("\n--- Valores actuales de sensores ---")
            for col in ultima_fila.index:
                print(f"{col}: {ultima_fila[col]}")

            # Generar haiku aleatorio basado en valores de sensores + offset
            v1, v2, v3 = generar_haiku(df_haikus, ultima_fila)
            print(f"\n--- NUEVO HAIKU ---")
            print(f"Verso 1: {v1}")
            print(f"Verso 2: {v2}")
            print(f"Verso 3: {v3}")

            # Enviar cada verso a su ESP32 correspondiente y esperar tiempo de scroll
            for verso, texto in zip(["verso1", "verso2", "verso3"], [v1, v2, v3]):
                if enviar_verso_tcp(sockets[verso], texto):
                    time.sleep(calcular_tiempo_scroll(texto))

            # Pausa aleatoria entre haikus
            pausa = random.uniform(10.0, 15.0)
            print(f"Esperando {pausa:.1f} segundos antes del próximo haiku...\n")
            time.sleep(pausa)

    except KeyboardInterrupt:
        print("\nEjecución interrumpida manualmente")
    finally:
        print("Cerrando conexiones TCP con todas las ESP32...")
        for s in sockets.values():
            try:
                s.shutdown(socket.SHUT_RDWR)
            except:
                pass
            s.close()
        print("Conexiones finalizadas")

if __name__ == "__main__":
    main()
