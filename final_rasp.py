import pandas as pd
import random
import time
import socket

# --- CONFIGURACIÓN DE RED ---
ESP32_IP = "192.168.50.29"  # Cambia por la IP real de tu ESP32
ESP32_PORT = 5000           # Puerto TCP del servidor en la ESP32

# --- CONFIGURACIÓN DE RANGOS ---
RANGOS = {
    "temp": (0, 56),
    "tds": (0, 56),
    "ec": (0, 56),
    "orp": (0, 56),
    "sal": (0, 56),
    "do": (0, 56),
    "turb": (0, 56),
    "ph": (0, 56),
}

def leer_datos_sensores(archivo_csv):
    """Lee los datos de sensores desde un CSV."""
    df = pd.read_csv(archivo_csv)
    return df

def leer_haikus(archivo_excel):
    """Lee la base de haikus desde un Excel."""
    df = pd.read_excel(archivo_excel)
    df.columns = df.columns.str.strip()
    return df

def seleccionar_verso(columna, valor_sensor, df_haikus):
    """Selecciona un verso basado en el valor del sensor."""
    minimo, maximo = RANGOS.get(columna, (0, len(df_haikus) - 1))
    idx_inicial = int((valor_sensor % (maximo - minimo + 1)) + minimo)
    idx_final = min(idx_inicial + 10, maximo)
    fila = random.randint(idx_inicial, idx_final)
    return df_haikus.iloc[fila][columna]

def generar_haiku(df_sensores, df_haikus):
    """Genera un haiku con los últimos datos de los sensores."""
    ultima_fila = df_sensores.iloc[-1]

    verso1 = seleccionar_verso("Verso 1 (5 sílabas)", ultima_fila["temp"], df_haikus)
    verso2 = seleccionar_verso("Verso 2 (7 sílabas)", ultima_fila["tds"], df_haikus)
    verso3 = seleccionar_verso("Verso 3 (5 sílabas)", ultima_fila["ph"], df_haikus)

    return verso1, verso2, verso3

def enviar_verso_tcp(verso):
    """Envía un verso a la ESP32 mediante TCP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Conectando a ESP32 en {ESP32_IP}:{ESP32_PORT}...")
            s.connect((ESP32_IP, ESP32_PORT))
            print("Conectado! Enviando verso...")

            mensaje = verso + "\n"
            s.sendall(mensaje.encode('utf-8'))

            respuesta = s.recv(1024).decode('utf-8')
            print("Respuesta de ESP32:", respuesta)
            print("Cerrando conexión...\n")
    except Exception as e:
        print(f"⚠️ Error al enviar verso TCP: {e}")

def main():
    archivo_csv = "aquarium_readings.csv"
    archivo_excel = "hidropoeticas_Haikus.xlsx"

    # Cargar datos
    df_sensores = leer_datos_sensores(archivo_csv)
    df_haikus = leer_haikus(archivo_excel)

    # Generar haiku
    v1, v2, v3 = generar_haiku(df_sensores, df_haikus)

    print("\n=== 🌸 HAIKU GENERADO 🌸 ===")
    print(v1)
    print(v2)
    print(v3)
    print("============================\n")

    # Enviar versos uno por uno a la ESP32
    for verso in [v1, v2, v3]:
        enviar_verso_tcp(verso)
        time.sleep(random.uniform(1.0, 3.0))

if __name__ == "__main__":
    main()
