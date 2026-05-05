"""
mock_robot.py
-------------
Simula el servidor TCP del robot (RAPID) para probar ClienteGoFa_imagen.py
sin necesidad de robot real.

USO:
  1. Arranca este script primero.
  2. En ClienteGoFa_imagen.py cambia la IP a 127.0.0.1:
       mi_socket.connect(("127.0.0.1", 1025))
  3. Arranca ClienteGoFa_imagen.py.
  4. Desde este terminal escribe comandos:
       C1  → simula HMI seleccionando Amarillo
       C2  → simula HMI seleccionando Azul
       C3  → simula HMI seleccionando Rojo
       q   → cerrar
"""

import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 1025

client_conn = None

def recibir_loop(conn):
    """Hilo que imprime las coordenadas que llegan de Python."""
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("[mock] Python cerro la conexion.")
                break
            msg = data.decode(errors="ignore").strip()
            if len(msg) == 6 and msg.isdigit():
                x, y = int(msg[:3]), int(msg[3:])
                print(f"[mock] Coordenadas recibidas: X={x} mm  Y={y} mm  (raw: {msg})")
            else:
                print(f"[mock] Mensaje recibido: {repr(msg)}")
        except Exception as e:
            print(f"[mock] Error recv: {e}")
            break

def main():
    global client_conn
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    print(f"[mock] Esperando conexion en {HOST}:{PORT} ...")

    conn, addr = srv.accept()
    client_conn = conn
    print(f"[mock] Python conectado desde {addr}")

    conn.sendall("GoFa connected succesfully".encode())
    bienvenida = conn.recv(1024).decode(errors="ignore").strip()
    print(f"[mock] Python envio: {repr(bienvenida)}")
    print()
    print("Comandos: C1=Amarillo  C2=Azul  C3=Rojo  q=salir")
    print("-" * 40)

    hilo = threading.Thread(target=recibir_loop, args=(conn,), daemon=True)
    hilo.start()

    while True:
        cmd = input().strip()
        if cmd.lower() == "q":
            break
        if cmd in ("C1", "C2", "C3"):
            conn.sendall(cmd.encode())
            nombres = {"C1": "Amarillo", "C2": "Azul", "C3": "Rojo"}
            print(f"[mock] Enviado {cmd} ({nombres[cmd]})")
        else:
            print("[mock] Comando no reconocido. Usa C1, C2, C3 o q.")

    conn.close()
    srv.close()
    print("[mock] Cerrado.")

if __name__ == "__main__":
    main()