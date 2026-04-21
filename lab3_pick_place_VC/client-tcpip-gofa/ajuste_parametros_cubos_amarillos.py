import cv2
import numpy as np
import json
import os
import sys
from pathlib import Path

# -------------------------------------------------
# Paths (compatible with Windows or WSL)
# -------------------------------------------------
BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "images" / "escenario1.jpg"
CONFIG_FILE = BASE_DIR / "config_cubos_amarillos.json"

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def nothing(x):
    pass

def cargar_config():
    """Load saved config if it exists, otherwise return defaults."""
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # defaults (same as first entry in yellow_cube_params.json)
    return {
        "hsv_lower_h": 20,
        "hsv_lower_s": 150,
        "hsv_lower_v": 150,
        "hsv_upper_h": 30,
        "hsv_upper_s": 255,
        "hsv_upper_v": 255,
        "min_area": 500
    }

def guardar_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    print(f"✅ Configuración guardada en {CONFIG_FILE}")

# -------------------------------------------------
# Load image
# -------------------------------------------------
img = cv2.imread(str(IMAGE_PATH))
if img is None:
    raise FileNotFoundError(f"No se encontró la imagen: {IMAGE_PATH}")
img = cv2.resize(img, (640, 480))

# -------------------------------------------------
# Load or initialise parameters
# -------------------------------------------------
params = cargar_config()

# -------------------------------------------------
# Create trackbars window
# -------------------------------------------------
cv2.namedWindow("Controles", cv2.WINDOW_NORMAL)
cv2.createTrackbar("H Min", "Controles", params.get("hsv_lower_h", 20), 179, nothing)
cv2.createTrackbar("S Min", "Controles", params.get("hsv_lower_s", 150), 255, nothing)
cv2.createTrackbar("V Min", "Controles", params.get("hsv_lower_v", 150), 255, nothing)
cv2.createTrackbar("H Max", "Controles", params.get("hsv_upper_h", 30), 179, nothing)
cv2.createTrackbar("S Max", "Controles", params.get("hsv_upper_s", 255), 255, nothing)
cv2.createTrackbar("V Max", "Controles", params.get("hsv_upper_v", 255), 255, nothing)
cv2.createTrackbar("Min Area", "Controles", params.get("min_area", 500), 5000, nothing)

print("=== Herramienta interactiva para ajustar detección de cubos amarillos ===")
print("Usa los sliders en la ventana 'Controles' y observa los resultados.")
print("Pulsa 's' para guardar la configuración actual, 'q' o ESC para salir.")

while True:
    # -------------------------------------------------
    # Read trackbar positions
    # -------------------------------------------------
    h_min = cv2.getTrackbarPos("H Min", "Controles")
    s_min = cv2.getTrackbarPos("S Min", "Controles")
    v_min = cv2.getTrackbarPos("V Min", "Controles")
    h_max = cv2.getTrackbarPos("H Max", "Controles")
    s_max = cv2.getTrackbarPos("S Max", "Controles")
    v_max = cv2.getTrackbarPos("V Max", "Controles")
    min_area = cv2.getTrackbarPos("Min Area", "Controles")

    lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper = np.array([h_max, s_max, v_max], dtype=np.uint8)

    # -------------------------------------------------
    # Process image
    # -------------------------------------------------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered = [c for c in contours if cv2.contourArea(c) >= min_area]

    vis = img.copy()
    cv2.drawContours(vis, filtered, -1, (0, 255, 255), 2)

    # -------------------------------------------------
    # Show results
    # -------------------------------------------------
    cv2.imshow("Deteccion", vis)
    cv2.imshow("Mascara", mask)

    key = cv2.waitKey(30) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('s'):
        cfg_to_save = {
            "hsv_lower_h": h_min,
            "hsv_lower_s": s_min,
            "hsv_lower_v": v_min,
            "hsv_upper_h": h_max,
            "hsv_upper_s": s_max,
            "hsv_upper_v": v_max,
            "min_area": min_area,
        }
        guardar_config(cfg_to_save)

cv2.destroyAllWindows()
