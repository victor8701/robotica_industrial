import cv2
import numpy as np
import json
import os
from pathlib import Path

# ─── SELECCIONA EL COLOR A CALIBRAR ───────────────────────────────────────────
COLOR = "rojo"   # "verde" | "amarillo" | "azul" | "rojo"
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "images" / "escenario3.jpg"
CONFIG_FILE = BASE_DIR / f"config_cubos_{COLOR}.json"

DEFAULTS = {
    "amarillo": {"hsv_lower_h": 20,  "hsv_lower_s": 150, "hsv_lower_v": 150,
                 "hsv_upper_h": 30,  "hsv_upper_s": 255, "hsv_upper_v": 255, "min_area": 500},
    "verde":    {"hsv_lower_h": 35,  "hsv_lower_s": 50,  "hsv_lower_v": 20,
                 "hsv_upper_h": 85,  "hsv_upper_s": 255, "hsv_upper_v": 255, "min_area": 800},
    "azul":     {"hsv_lower_h": 100, "hsv_lower_s": 100, "hsv_lower_v": 20,
                 "hsv_upper_h": 125, "hsv_upper_s": 255, "hsv_upper_v": 255, "min_area": 3000},
    "rojo":     {"hsv_lower_h": 0,   "hsv_lower_s": 100, "hsv_lower_v": 20,
                 "hsv_upper_h": 5,   "hsv_upper_s": 255, "hsv_upper_v": 255,
                 "hsv_lower_h2": 175, "hsv_upper_h2": 179, "min_area": 3000},
}

def cargar_config():
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULTS[COLOR]

def guardar_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    print(f"Configuracion guardada en {CONFIG_FILE}")

img = cv2.imread(str(IMAGE_PATH))
if img is None:
    raise FileNotFoundError(f"No se encontro la imagen: {IMAGE_PATH}")
img = cv2.resize(img, (640, 480))

params = cargar_config()
es_rojo = (COLOR == "rojo")

cv2.namedWindow("Controles", cv2.WINDOW_NORMAL)
cv2.createTrackbar("H Min",    "Controles", params.get("hsv_lower_h", 0),   179, lambda x: None)
cv2.createTrackbar("S Min",    "Controles", params.get("hsv_lower_s", 100), 255, lambda x: None)
cv2.createTrackbar("V Min",    "Controles", params.get("hsv_lower_v", 20),  255, lambda x: None)
cv2.createTrackbar("H Max",    "Controles", params.get("hsv_upper_h", 10),  179, lambda x: None)
cv2.createTrackbar("S Max",    "Controles", params.get("hsv_upper_s", 255), 255, lambda x: None)
cv2.createTrackbar("V Max",    "Controles", params.get("hsv_upper_v", 255), 255, lambda x: None)
cv2.createTrackbar("Min Area", "Controles", params.get("min_area", 500),   5000, lambda x: None)
if es_rojo:
    cv2.createTrackbar("H Min2", "Controles", params.get("hsv_lower_h2", 175), 179, lambda x: None)
    cv2.createTrackbar("H Max2", "Controles", params.get("hsv_upper_h2", 179), 179, lambda x: None)

COLOR_BGR_MAP = {"amarillo": (0, 255, 255), "azul": (255, 0, 0), "rojo": (0, 0, 255), "verde": (0, 255, 0)}
color_bgr = COLOR_BGR_MAP[COLOR]

print(f"=== Calibracion de cubos {COLOR} ===")
print("Ajusta los sliders y pulsa 's' para guardar, 'q'/ESC para salir.")

while True:
    h_min  = cv2.getTrackbarPos("H Min",    "Controles")
    s_min  = cv2.getTrackbarPos("S Min",    "Controles")
    v_min  = cv2.getTrackbarPos("V Min",    "Controles")
    h_max  = cv2.getTrackbarPos("H Max",    "Controles")
    s_max  = cv2.getTrackbarPos("S Max",    "Controles")
    v_max  = cv2.getTrackbarPos("V Max",    "Controles")
    min_area = cv2.getTrackbarPos("Min Area", "Controles")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([h_min, s_min, v_min], np.uint8),
                            np.array([h_max, s_max, v_max], np.uint8))
    if es_rojo:
        h_min2 = cv2.getTrackbarPos("H Min2", "Controles")
        h_max2 = cv2.getTrackbarPos("H Max2", "Controles")
        mask2 = cv2.inRange(hsv, np.array([h_min2, s_min, v_min], np.uint8),
                                 np.array([h_max2, s_max, v_max], np.uint8))
        mask = cv2.add(mask, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vis = img.copy()
    overlay = vis.copy()
    for c in contours:
        if cv2.contourArea(c) >= min_area:
            hull = cv2.convexHull(c)
            cv2.fillPoly(overlay, [hull], color_bgr)
            cv2.drawContours(vis, [hull], 0, color_bgr, 2)
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                cv2.circle(vis, (cx, cy), 7, color_bgr, -1)
    cv2.addWeighted(overlay, 0.35, vis, 0.65, 0, vis)

    cv2.imshow("Deteccion", vis)
    cv2.imshow("Mascara", mask)

    key = cv2.waitKey(30) & 0xFF
    if key in (ord('q'), 27):
        break
    elif key == ord('s'):
        cfg_to_save = {
            "hsv_lower_h": h_min, "hsv_lower_s": s_min, "hsv_lower_v": v_min,
            "hsv_upper_h": h_max, "hsv_upper_s": s_max, "hsv_upper_v": v_max,
            "min_area": min_area,
        }
        if es_rojo:
            cfg_to_save["hsv_lower_h2"] = h_min2
            cfg_to_save["hsv_upper_h2"] = h_max2
        guardar_config(cfg_to_save)

cv2.destroyAllWindows()