import cv2
import numpy as np
import socket
import time
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config_cubos_amarillos.json"

# ─────────────────────────────────────────────
#  VARIABLE GLOBAL DE MODO DE CAPTURA
#  True  → usa la cámara (índice 1)
#  False → usa la imagen estática images/escenario1.jpg
# ─────────────────────────────────────────────
USAR_CAMARA = False

# ─────────────────────────────────────────────
#  VARIABLE GLOBAL DE CONEXIÓN AL ROBOT
#  True  → conecta al robot por TCP/IP (uso en laboratorio)
#  False → modo offline, sin socket (pruebas desde casa)
# ─────────────────────────────────────────────
CONECTAR_ROBOT = False

if CONECTAR_ROBOT:
    mi_socket = socket.socket()
    mi_socket.connect(("192.168.1.89", 1025))
    respuesta = mi_socket.recv(1024)
    print(respuesta)
    mi_socket.sendall('Server connected'.encode())
else:
    mi_socket = None
    print("[OFFLINE] Sin conexión al robot.")


def dibujar(mask, color, min_area=3000):
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    for c in contornos:
        area = cv2.contourArea(c)
        if area > min_area:
            M = cv2.moments(c)
            if (M["m00"] == 0):
                M["m00"] = 1
            x = int(M["m10"] / M["m00"])
            y = int(M['m01'] / M['m00'])
            nuevoContorno = cv2.convexHull(c)
            cv2.circle(frame, (x, y), 7, color, -1)
            cv2.putText(frame, '{},{}'.format(x, y), (x + 10, y), font, 0.75,
                        color, 1, cv2.LINE_AA)
            cv2.drawContours(frame, [nuevoContorno], 0, color, 3)
            coorX = ''
            coorY = ''
            if x < 100:
                coorX = '0' + str(x)
            else:
                coorX = str(x)
            if y < 100:
                coorY = '0' + str(y)
            else:
                coorY = str(y)
            coordXY = coorX + coorY
            if mi_socket:
                mi_socket.sendall(coordXY.encode())
                time.sleep(1)
            print("Coordenadas: " + coordXY)


# ─────────────────────────────────────────────
#  Inicialización de la fuente de imagen
# ─────────────────────────────────────────────
IMAGEN_ESTATICA = "images/escenario1.jpg"

if USAR_CAMARA:
    cap = cv2.VideoCapture(1)
    # Set desired frame size for camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
else:
    # Carga la imagen una sola vez
    img_estatica = cv2.imread(IMAGEN_ESTATICA)
    if img_estatica is None:
        raise FileNotFoundError(
            f"No se encontró la imagen: {IMAGEN_ESTATICA}")
    # Resize static image to match expected processing size
    img_estatica = cv2.resize(img_estatica, (640, 480))

azulBajo = np.array([100, 100, 20], np.uint8)
azulAlto = np.array([125, 255, 255], np.uint8)

# Cargar parámetros de cubos amarillos si existe el config
if CONFIG_FILE.is_file():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    amarilloBajo = np.array([cfg.get("hsv_lower_h", 20), cfg.get("hsv_lower_s", 150), cfg.get("hsv_lower_v", 150)], np.uint8)
    amarilloAlto = np.array([cfg.get("hsv_upper_h", 30), cfg.get("hsv_upper_s", 255), cfg.get("hsv_upper_v", 255)], np.uint8)
    min_area_amarillo = cfg.get("min_area", 500)
else:
    amarilloBajo = np.array([20, 150, 150], np.uint8)
    amarilloAlto = np.array([30, 255, 255], np.uint8)
    min_area_amarillo = 3000

redBajo1 = np.array([0, 100, 20], np.uint8)
redAlto1 = np.array([5, 255, 255], np.uint8)
redBajo2 = np.array([175, 100, 20], np.uint8)
redAlto2 = np.array([179, 255, 255], np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    if USAR_CAMARA:
        ret, frame = cap.read()
    else:
        # Simula ret=True con una copia de la imagen estática
        ret = True
        frame = img_estatica.copy()

    if ret:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        maskAzul = cv2.inRange(frameHSV, azulBajo, azulAlto)
        maskAmarillo = cv2.inRange(frameHSV, amarilloBajo, amarilloAlto)
        maskRed1 = cv2.inRange(frameHSV, redBajo1, redAlto1)
        maskRed2 = cv2.inRange(frameHSV, redBajo2, redAlto2)
        maskRed = cv2.add(maskRed1, maskRed2)
        # dibujar(maskAzul, (255, 0, 0))
        dibujar(maskAmarillo, (0, 255, 255), min_area=min_area_amarillo)
        # dibujar(maskRed, (0, 0, 255))
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            if mi_socket:
                mi_socket.close()
            break

if USAR_CAMARA:
    cap.release()
cv2.destroyAllWindows()
