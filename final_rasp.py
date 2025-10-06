import pandas as pd
import random
import time
import socket

# --- CONFIGURACIÓN TCP DE CADA ESP32 ---
ESP32_IPS = {
    "verso1": "192.168.50.101",  # Pantalla 1
    "verso2": "192.168.50.102",  # Pantalla 2
    "verso3": "192.168.50.103",  # Pantalla 3
}
ESP32_PORT = 5000

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

# --- PARÁMETROS DE SCROLL ---
PIXELS_POR_CARACTER = 6
SCROLL_SPEED = 50
PANEL_WIDTH = 128

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
    v1 = seleccionar_verso("Verso 1 (5 sílabas)", ultima_fila["temp"], df_haikus)
    v2 = seleccionar_verso("Verso 2 (7 sílabas)", ultima_fila["tds"], df_haikus)
    v3 = seleccionar_verso("Verso 3 (5 sílabas)", ultima_fila["ph"], df_haikus)
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
    ancho_verso = len(verso) * PIXELS_POR_CARACTER
    if ancho_verso <= PANEL_WIDTH:
        return 2.0  # mostrar al menos 2 seg si cabe completo
    else:
        pasos_scroll = ancho_verso + PANEL_WIDTH
        return pasos_scroll * SCROLL_SPEED / 1000

def main():
    archivo_csv = "aquarium_readings.csv"
    archivo_excel = "Hidropoeticas_Haikus.xlsx"

    df_sensores = leer_datos_sensores(archivo_csv)
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
            v1, v2, v3 = generar_haiku(df_sensores, df_haikus)
            print(f"\n--- NUEVO HAIKU ---")
            print(f"Verso 1: {v1}")
            print(f"Verso 2: {v2}")
            print(f"Verso 3: {v3}")

            # Enviar cada verso a su ESP32 correspondiente y esperar tiempo de scroll
            for verso, texto in zip(["verso1", "verso2", "verso3"], [v1, v2, v3]):
                if enviar_verso_tcp(sockets[verso], texto):
                    time.sleep(calcular_tiempo_scroll(texto))

            # Pausa aleatoria entre haikus
            pausa = random.uniform(5.0, 15.0)
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
