import socket
import time

HOST = "192.168.50.29"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"Intentando conectar a {HOST}:{PORT}...")
    s.connect((HOST, PORT))
    print("Conectado!")

    while True:
        msg = input("Mensaje para ESP32 (o 'salir'): ")
        if msg.lower() == "salir":
            break

        s.sendall((msg + "\n").encode())
        data = s.recv(1024)
        print("Respuesta del ESP32:", data.decode())

    print("Cerrando conexión...")
