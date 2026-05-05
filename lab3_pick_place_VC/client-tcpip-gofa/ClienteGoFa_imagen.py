import cv2
import numpy as np
import socket
import select
import time
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent
HOMOGRAPHY_FILE = BASE_DIR / "homography.json"

COLOR_CONFIG_FILES = {
    1: BASE_DIR / "config_cubos_amarillos.json",
    2: BASE_DIR / "config_cubos_azul.json",
    3: BASE_DIR / "config_cubos_rojo.json",
}
COLOR_BGR = {1: (0, 255, 255), 2: (255, 0, 0), 3: (0, 0, 255)}
COLOR_DEFAULTS = {
    1: {"hsv_lower_h": 20,  "hsv_lower_s": 150, "hsv_lower_v": 150,
        "hsv_upper_h": 30,  "hsv_upper_s": 255, "hsv_upper_v": 255, "min_area": 3000},
    2: {"hsv_lower_h": 100, "hsv_lower_s": 100, "hsv_lower_v": 20,
        "hsv_upper_h": 125, "hsv_upper_s": 255, "hsv_upper_v": 255, "min_area": 3000},
    3: {"hsv_lower_h": 0,   "hsv_lower_s": 100, "hsv_lower_v": 20,
        "hsv_upper_h": 5,   "hsv_upper_s": 255, "hsv_upper_v": 255,
        "hsv_lower_h2": 175, "hsv_upper_h2": 179, "min_area": 3000},
}


# ─────────────────────────────────────────────
#  FUNCIONES DE HOMOGRAFÍA (píxel → mm robot)
# ─────────────────────────────────────────────

def cargar_homografia(ruta):
    """Lee homography.json generado por calibrar_homografia.py.
    Devuelve la matriz H (3×3, float64), o None si el fichero no existe."""
    if not Path(ruta).is_file():
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)
    return np.array(data["H"], dtype=np.float64)


def pixel_a_mm(px, py, H):
    """Aplica la homografía H para convertir (px, py) en píxeles
    a (x_mm, y_mm) en el frame del robot (Workobject_1)."""
    pt = np.array([[[px, py]]], dtype=np.float32)
    resultado = cv2.perspectiveTransform(pt, H)[0][0]
    return float(resultado[0]), float(resultado[1])


def formatear_coordenadas(x_mm, y_mm):
    """Convierte (x_mm, y_mm) a string de 6 chars 'XXXYYYY' compatible con RAPID.
    Redondea a entero y hace clamp al rango [0, 999]."""
    x = max(0, min(999, int(round(x_mm))))
    y = max(0, min(999, int(round(y_mm))))
    return f"{x:03d}{y:03d}"


def _cfg_color(color_id):
    ruta = COLOR_CONFIG_FILES[color_id]
    if Path(ruta).is_file():
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return COLOR_DEFAULTS[color_id]

def calcular_mask(frameHSV, cfg):
    lo = np.array([cfg["hsv_lower_h"], cfg["hsv_lower_s"], cfg["hsv_lower_v"]], np.uint8)
    hi = np.array([cfg["hsv_upper_h"], cfg["hsv_upper_s"], cfg["hsv_upper_v"]], np.uint8)
    mask = cv2.inRange(frameHSV, lo, hi)
    if "hsv_lower_h2" in cfg:
        lo2 = np.array([cfg["hsv_lower_h2"], cfg["hsv_lower_s"], cfg["hsv_lower_v"]], np.uint8)
        hi2 = np.array([cfg["hsv_upper_h2"], cfg["hsv_upper_s"], cfg["hsv_upper_v"]], np.uint8)
        mask = cv2.add(mask, cv2.inRange(frameHSV, lo2, hi2))
    return mask

color_configs = {cid: _cfg_color(cid) for cid in (1, 2, 3)}

# Color seleccionado por el HMI (1=amarillo, 2=azul, 3=rojo)
# RAPID envia "C{n}" por TCP cuando el operario pulsa INICIAR
selected_color_global = 1
COLOR_NOMBRES = {1: "Amarillo", 2: "Azul", 3: "Rojo"}

def leer_color_desde_rapid():
    """Lee el color enviado por RAPID ('C1'/'C2'/'C3') sin bloquear."""
    global selected_color_global
    if mi_socket is None:
        return
    try:
        readable, _, _ = select.select([mi_socket], [], [], 0)
        if readable:
            data = mi_socket.recv(8).decode(errors="ignore").strip()
            if data.startswith("C") and len(data) >= 2 and data[1].isdigit():
                nuevo = int(data[1])
                if nuevo in (1, 2, 3):
                    selected_color_global = nuevo
                    print(f"[HMI] Color recibido: {COLOR_NOMBRES[selected_color_global]}")
    except Exception as e:
        print(f"[HMI] Error leyendo color: {e}")

# variable camara ordenador (1) o externa (0)
camara = 0

# ─────────────────────────────────────────────
#  VARIABLE GLOBAL DE MODO DE CAPTURA
#  True  → usa la cámara (índice 1)
#  False → usa la imagen estática images/escenario1.jpg
# ─────────────────────────────────────────────
USAR_CAMARA = True

# ─────────────────────────────────────────────
#  VARIABLE GLOBAL DE CONEXIÓN AL ROBOT
#  True  → conecta al robot por TCP/IP (uso en laboratorio)
#  False → modo offline, sin socket (pruebas desde casa)
# ─────────────────────────────────────────────
CONECTAR_ROBOT = True

if CONECTAR_ROBOT:
    mi_socket = socket.socket()
    mi_socket.connect(("192.168.125.1", 1025))
    #mi_socket.connect(("127.0.0.1", 1025)) #para prueba sin robot con mock_robot.py
    respuesta = mi_socket.recv(1024)
    print(respuesta)
    mi_socket.sendall('Server connected'.encode())
else:
    mi_socket = None
    print("[OFFLINE] Sin conexión al robot.")

# Cargar homografía de calibración
H_global = cargar_homografia(HOMOGRAPHY_FILE)
if H_global is not None:
    print("[CALIB] Homografía cargada correctamente.")
else:
    print("[AVISO] homography.json no encontrado. Ejecuta calibrar_homografia.py.")
    print("        Las coordenadas enviadas al robot serán en píxeles (incorrecto).")


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
            cv2.drawContours(frame, [nuevoContorno], 0, color, 3)

            if H_global is not None:
                x_mm, y_mm = pixel_a_mm(x, y, H_global)
                coordXY = formatear_coordenadas(x_mm, y_mm)
                label = f'{x},{y}px -> {x_mm:.0f},{y_mm:.0f}mm (wobj0)'
            else:
                coordXY = f"{x:03d}{y:03d}"
                label = f'{x},{y}px (sin calib)'

            cv2.putText(frame, label, (x + 10, y), font, 0.65,
                        color, 1, cv2.LINE_AA)

            if mi_socket:
                mi_socket.sendall(coordXY.encode())
                time.sleep(1)
            print("Coordenadas: " + coordXY)


# ─────────────────────────────────────────────
#  Inicialización de la fuente de imagen
# ─────────────────────────────────────────────
IMAGEN_ESTATICA = BASE_DIR / "images" / "escenario1.jpg"

if USAR_CAMARA:
    cap = cv2.VideoCapture(camara)
    # Set desired frame size for camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
else:
    # Carga la imagen una sola vez
    img_estatica = cv2.imread(str(IMAGEN_ESTATICA))
    if img_estatica is None:
        raise FileNotFoundError(
            f"No se encontró la imagen: {IMAGEN_ESTATICA}")
    # Resize static image to match expected processing size
    img_estatica = cv2.resize(img_estatica, (640, 480))

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

        leer_color_desde_rapid()

        cfg_activo = color_configs[selected_color_global]
        mask = calcular_mask(frameHSV, cfg_activo)
        dibujar(mask, COLOR_BGR[selected_color_global], min_area=cfg_activo.get("min_area", 3000))

        cv2.putText(frame, f"Buscando: {COLOR_NOMBRES[selected_color_global]}",
                    (10, 25), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            if mi_socket:
                mi_socket.close()
            break

if USAR_CAMARA:
    cap.release()
cv2.destroyAllWindows()
