import pandas as pd
import random
import time
import socket

# --- CONFIGURACIÓN TCP ---
ESP32_IP = "192.168.50.29"  # ← cambia esta por la IP real de tu ESP32
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

def enviar_verso_tcp(socket_cliente, verso):
    try:
        mensaje = f"{verso}\n"
        socket_cliente.sendall(mensaje.encode('utf-8'))
        print(f"Enviado a ESP32: {verso}")
        respuesta = socket_cliente.recv(1024)
        print("Respuesta:", respuesta.decode().strip())
        return True
    except Exception as e:
        print(f"Error enviando verso: {e}")
        return False

def main():
    archivo_csv = "aquarium_readings.csv"
    archivo_excel = "Hidropoeticas_Haikus.xlsx"

    # Leer archivos
    df_sensores = leer_datos_sensores(archivo_csv)
    df_haikus = leer_haikus(archivo_excel)

    print(f"Conectando a ESP32 en {ESP32_IP}:{ESP32_PORT}...")

    # Crear conexión TCP persistente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ESP32_IP, ESP32_PORT))
        print("Conectado correctamente a ESP32 🟢\n")

        print("=== INICIO DEL CICLO INFINITO DE HAIKUS ===\n")
        try:
            while True:
                v1, v2, v3 = generar_haiku(df_sensores, df_haikus)

                print(f"Verso 1: {v1}")
                print(f"Verso 2: {v2}")
                print(f"Verso 3: {v3}")

                # Enviar versos con pausas aleatorias
                if enviar_verso_tcp(s, v1):
                    time.sleep(random.uniform(1.0, 4.0))

                if enviar_verso_tcp(s, v2):
                    time.sleep(random.uniform(1.0, 4.0))

                if enviar_verso_tcp(s, v3):
                    time.sleep(random.uniform(1.0, 4.0))

                pausa = random.uniform(5.0, 15.0)
                print(f"Esperando {pausa:.1f} segundos antes del próximo haiku...\n")
                time.sleep(pausa)

        except KeyboardInterrupt:
            print("\n--- Ejecución interrumpida manualmente ---")

        finally:
            print("Cerrando conexión TCP con ESP32...")
            s.close()
            print("Conexión finalizada 🔴")

if __name__ == "__main__":
    main()
