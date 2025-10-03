import socket

HOST = "192.168.50.29"  # IP de la ESP32 (revísala en el Serial Monitor)
PORT = 5000             # Puerto del servidor en ESP32

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hola ESP32 desde Raspberry Pi!\n")
