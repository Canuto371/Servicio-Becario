import socket

HOST = "192.168.50.29"  # Revisa que sea la IP correcta
PORT = 5000

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)  # evita que se quede colgado
        print(f"Intentando conectar a {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Conectado! Enviando mensaje...")
        s.sendall(b"Hola ESP32 desde Raspberry Pi!\n")
        
        # Leer respuesta del ESP32
        data = s.recv(1024)
        print("Respuesta del ESP32:", data.decode())
except Exception as e:
    print("Error de conexión:", e)
