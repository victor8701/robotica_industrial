import cv2
import numpy as np
import socket
import select
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
HOMOGRAPHY_FILE = BASE_DIR / "homography.json"

mi_socket = socket.socket()
mi_socket.connect(("192.168.125.1", 1025))
#mi_socket.connect(("127.0.0.1", 1025))
respuesta = mi_socket.recv(1024)
print(respuesta)
mi_socket.sendall('Server connected'.encode())

# ─── HOMOGRAFÍA ───────────────────────────────────────────────────────────────

def cargar_homografia(ruta):
    if not Path(ruta).is_file():
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)
    return np.array(data["H"], dtype=np.float64)

H_global = cargar_homografia(HOMOGRAPHY_FILE)
if H_global is None:
    print("[AVISO] homography.json no encontrado. Coordenadas en pixeles.")

def pixel_a_mm(px, py):
    pt = np.array([[[px, py]]], dtype=np.float32)
    res = cv2.perspectiveTransform(pt, H_global)[0][0]
    return float(res[0]), float(res[1])

def formatear_coords(x_mm, y_mm):
    x = max(0, min(999, int(round(x_mm))))
    y = max(0, min(999, int(round(y_mm))))
    return f"{x:03d}{y:03d}"

# ─── CONFIGURACIÓN DE COLORES ─────────────────────────────────────────────────
# Valores por defecto si no existe el JSON calibrado
DEFAULTS = {
    "amarillo": {"hsv_lower_h": 20,  "hsv_lower_s": 150, "hsv_lower_v": 150,
                 "hsv_upper_h": 30,  "hsv_upper_s": 255, "hsv_upper_v": 255, "min_area": 1000},
    "verde":    {"hsv_lower_h": 45,  "hsv_lower_s": 75,  "hsv_lower_v": 52,
                 "hsv_upper_h": 85,  "hsv_upper_s": 189, "hsv_upper_v": 147, "min_area": 442},
    "azul":     {"hsv_lower_h": 96,  "hsv_lower_s": 69,  "hsv_lower_v": 0,
                 "hsv_upper_h": 117, "hsv_upper_s": 198, "hsv_upper_v": 255, "min_area": 986},
    "rojo":     {"hsv_lower_h": 0,   "hsv_lower_s": 128, "hsv_lower_v": 132,
                 "hsv_upper_h": 49,  "hsv_upper_s": 255, "hsv_upper_v": 255,
                 "hsv_lower_h2": 145, "hsv_upper_h2": 179, "min_area": 136},
}

# C1=Amarillo  C2=Azul  C3=Rojo  C4=Verde
COLOR_IDS   = {1: "amarillo", 2: "azul", 3: "rojo", 4: "verde"}
COLOR_BGR   = {"amarillo": (0, 255, 255), "azul": (255, 0, 0), "rojo": (0, 0, 255), "verde": (0, 200, 0)}
COLOR_NOMBRES = {1: "Amarillo", 2: "Azul", 3: "Rojo", 4: "Verde"}

def _cargar_cfg(nombre):
    ruta = BASE_DIR / f"config_cubos_{nombre}.json"
    if ruta.is_file():
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULTS[nombre]

color_configs = {cid: _cargar_cfg(nombre) for cid, nombre in COLOR_IDS.items()}

def calcular_mask(frameHSV, cfg):
    lo = np.array([cfg["hsv_lower_h"], cfg["hsv_lower_s"], cfg["hsv_lower_v"]], np.uint8)
    hi = np.array([cfg["hsv_upper_h"], cfg["hsv_upper_s"], cfg["hsv_upper_v"]], np.uint8)
    mask = cv2.inRange(frameHSV, lo, hi)
    if "hsv_lower_h2" in cfg:
        lo2 = np.array([cfg["hsv_lower_h2"], cfg["hsv_lower_s"], cfg["hsv_lower_v"]], np.uint8)
        hi2 = np.array([cfg["hsv_upper_h2"], cfg["hsv_upper_s"], cfg["hsv_upper_v"]], np.uint8)
        mask = cv2.add(mask, cv2.inRange(frameHSV, lo2, hi2))
    return mask

# ─── ESTADO: color pedido por RAPID ───────────────────────────────────────────
selected_color_id = None  # ultimo color solicitado por RAPID
pendiente_envio = False   # True = RAPID espera una coordenada

def leer_color_desde_rapid():
    """Lee mensajes de RAPID: 'Cn' (peticion de coordenada) o 'FIN' (9 piezas completadas)."""
    global selected_color_id, pendiente_envio
    try:
        readable, _, _ = select.select([mi_socket], [], [], 0)
        if readable:
            data = mi_socket.recv(8).decode(errors="ignore").strip()
            if data == "FIN":
                print("\n" + "=" * 45)
                print("  COMPLETADO: 9 piezas recogidas con exito.")
                print("=" * 45 + "\n")
            elif data.startswith("C") and len(data) >= 2 and data[1].isdigit():
                nuevo = int(data[1])
                if nuevo in COLOR_IDS:
                    selected_color_id = nuevo
                    pendiente_envio = True
                    print(f"\n[RAPID] Peticion: {COLOR_NOMBRES[nuevo]} — buscando pieza...")
    except Exception as e:
        print(f"[Error] Socket: {e}")

# ─── DETECCIÓN + DIBUJO ───────────────────────────────────────────────────────
font = cv2.FONT_HERSHEY_SIMPLEX

def dibujar_color(frame, frameHSV, color_id):
    """Dibuja contornos y etiquetas de coordenadas del color dado.
    Devuelve lista de strings 'XXXYYYY' de las piezas en zona de recogida."""
    cfg = color_configs[color_id]
    mask = calcular_mask(frameHSV, cfg)
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bgr = COLOR_BGR[COLOR_IDS[color_id]]
    min_area = cfg.get("min_area", 500)
    coords_encontradas = []

    for c in contornos:
        if cv2.contourArea(c) < min_area:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
        hull = cv2.convexHull(c)
        cv2.drawContours(frame, [hull], 0, bgr, 3)
        cv2.circle(frame, (x, y), 7, bgr, -1)

        if H_global is not None:
            x_mm, y_mm = pixel_a_mm(x, y)
            if x_mm < 500:  # ignorar zona de deposito
                continue
            coordXY = formatear_coords(x_mm, y_mm)
            label = f'{coordXY[:3]},{coordXY[3:]}mm'
        else:
            coordXY = f"{x:03d}{y:03d}"
            label = f'{x},{y}px'

        cv2.putText(frame, label, (x + 10, y), font, 0.6, bgr, 1, cv2.LINE_AA)
        coords_encontradas.append(coordXY)

    return coords_encontradas

# ─── CAMARA ───────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)

print("\n=== Pick & Place - Vision ===")
print("Detectando colores. Esperando peticion de RAPID (INICIAR en HMI).")
print("Pulsa 's' para salir.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Comprobar si RAPID ha pedido una coordenada (no bloqueante)
    leer_color_desde_rapid()

    # Dibujar TODOS los colores con sus coordenadas en camara
    coords_seleccionado = []
    for cid in COLOR_IDS:
        coords = dibujar_color(frame, frameHSV, cid)
        if cid == selected_color_id:
            coords_seleccionado = coords

    # Overlay de estado
    if selected_color_id is None:
        estado = "Esperando HMI — pulsa INICIAR"
        color_estado = (200, 200, 200)
    elif pendiente_envio:
        estado = f"Buscando: {COLOR_NOMBRES[selected_color_id]}..."
        color_estado = COLOR_BGR[COLOR_IDS[selected_color_id]]
    else:
        estado = f"Listo — ultimo: {COLOR_NOMBRES[selected_color_id]}"
        color_estado = (180, 255, 180)
    cv2.putText(frame, estado, (10, 25), font, 0.65, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(frame, estado, (10, 25), font, 0.65, color_estado, 1, cv2.LINE_AA)

    # Aviso si RAPID espera pero no hay piezas visibles
    if pendiente_envio and not coords_seleccionado and selected_color_id is not None:
        aviso = f"SIN PIEZAS {COLOR_NOMBRES[selected_color_id].upper()} VISIBLES"
        cv2.putText(frame, aviso, (10, 55), font, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('frame', frame)

    # Responder a la peticion de RAPID: enviar UNA coordenada del color solicitado
    if pendiente_envio and coords_seleccionado:
        coordXY = coords_seleccionado[0]
        mi_socket.sendall(coordXY.encode())
        pendiente_envio = False
        print(f"Coordenada enviada [{COLOR_NOMBRES[selected_color_id]}]: {coordXY}")

    if cv2.waitKey(1) & 0xFF == ord('s'):
        mi_socket.close()
        break

cap.release()
cv2.destroyAllWindows()
