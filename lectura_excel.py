import pandas as pd
import random
import time
import serial
import serial.tools.list_ports

# --- CONFIGURACIÓN DE RANGOS ---
# Puedes ajustar estos rangos como quieras
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

# Configuración de puertos seriales para los ESP32
ESP32_PORTS = {
    "verso1": "/dev/ttyUSB0",  # Puerto para el primer verso (5 sílabas)
    "verso2": "/dev/ttyUSB1",  # Puerto para el segundo verso (7 sílabas)
    "verso3": "/dev/ttyUSB2"   # Puerto para el tercer verso (5 sílabas)
}

# Configuración serial (ajusta según tus necesidades)
SERIAL_CONFIG = {
    'baudrate': 9600,
    'timeout': 1
}

def detectar_puertos_seriales():
    """Detecta los puertos seriales disponibles"""
    puertos = [port.device for port in serial.tools.list_ports.comports()]
    print("Puertos seriales detectados:", puertos)
    return puertos

def inicializar_conexiones_seriales():
    """Inicializa las conexiones seriales con los ESP32"""
    conexiones = {}
    
    for nombre, puerto in ESP32_PORTS.items():
        try:
            conexiones[nombre] = serial.Serial(puerto, **SERIAL_CONFIG)
            time.sleep(2)  # Espera para inicialización
            print(f"Conexión establecida con {nombre} en {puerto}")
        except Exception as e:
            print(f"Error conectando a {nombre} en {puerto}: {e}")
            conexiones[nombre] = None
    
    return conexiones

def enviar_verso(conexion, verso):
    """Envía un verso a través de la conexión serial"""
    if conexion and conexion.is_open:
        try:
            # Asegurarse de que el verso termine con un newline
            mensaje = f"{verso}\n"
            conexion.write(mensaje.encode('utf-8'))
            print(f"Enviado: {verso}")
            return True
        except Exception as e:
            print(f"Error enviando verso: {e}")
            return False
    else:
        print("Conexión serial no disponible")
        return False

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
    """
    Selecciona un verso de una columna basado en el valor del sensor.
    Usa el valor del sensor para generar un rango y seleccionar aleatoriamente una fila.
    """
    minimo, maximo = RANGOS.get(columna, (0, len(df_haikus) - 1))

    # Normaliza el valor del sensor a un rango de índices
    idx_inicial = int((valor_sensor % (maximo - minimo + 1)) + minimo)
    idx_final = min(idx_inicial + 10, maximo)  # rango de 10 filas "alrededor" del valor

    fila = random.randint(idx_inicial, idx_final)
    return df_haikus.iloc[fila][columna]

def generar_haiku(df_sensores, df_haikus):
    """Genera un haiku en base a los datos de los sensores."""
    ultima_fila = df_sensores.iloc[-1]  # toma los últimos valores de sensores

    verso1 = seleccionar_verso("Verso 1 (5 sílabas)", ultima_fila["temp"], df_haikus)
    verso2 = seleccionar_verso("Verso 2 (7 sílabas)", ultima_fila["tds"], df_haikus)
    verso3 = seleccionar_verso("Verso 3 (5 sílabas)", ultima_fila["ph"], df_haikus)

    return verso1, verso2, verso3

def main():
    archivo_csv = "aquarium_readings.csv"
    archivo_excel = "hidropoeticas_Haikus.xlsx"

    # Detectar puertos disponibles
    puertos_disponibles = detectar_puertos_seriales()
    print("Puertos disponibles:", puertos_disponibles)

    # Inicializar conexiones seriales
    conexiones = inicializar_conexiones_seriales()

    # Cargar datos
    df_sensores = leer_datos_sensores(archivo_csv)
    df_haikus = leer_haikus(archivo_excel)

    # Generar haiku
    v1, v2, v3 = generar_haiku(df_sensores, df_haikus)
    
    print("\n=== HAIKU GENERADO ===")
    print(f"Verso 1: {v1}")
    print(f"Verso 2: {v2}")
    print(f"Verso 3: {v3}")
    print("=====================\n")

    # Enviar versos a los ESP32 correspondientes
    print("Enviando versos a los ESP32...")
    
    # Enviar verso 1 al primer ESP32
    if enviar_verso(conexiones.get("verso1"), v1):
        time.sleep(random.uniform(1.0, 3.0))
    
    # Enviar verso 2 al segundo ESP32
    if enviar_verso(conexiones.get("verso2"), v2):
        time.sleep(random.uniform(1.0, 3.0))
    
    # Enviar verso 3 al tercer ESP32
    if enviar_verso(conexiones.get("verso3"), v3):
        time.sleep(random.uniform(1.0, 3.0))

    # Cerrar conexiones
    for nombre, conexion in conexiones.items():
        if conexion and conexion.is_open:
            conexion.close()
            print(f"Conexión {nombre} cerrada")

if __name__ == "__main__":
    main()