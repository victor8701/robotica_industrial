"""
calibrar_homografia.py
----------------------
Herramienta interactiva para calcular la homografía píxel → mm del robot.

CÓMO USAR:
  1. Mide el área de trabajo con cinta métrica y rellena ROBOT_PTS con las
     coordenadas (x_mm, y_mm) de cada marca física en el frame de Workobject_1.
  2. Coloca marcas físicas visibles en la mesa (cinta adhesiva, etc.) en esas posiciones.
  3. Ejecuta el script. Con la cámara fija en su posición definitiva (o usando
     la imagen estática), haz clic sobre cada marca EN EL ORDEN de ROBOT_PTS.
  4. Cuando hayas clicado todos los puntos, pulsa 'c' → calcula H y guarda homography.json.
  5. Pulsa 'v' para entrar en modo verificación: haz clic en cualquier punto
     y verás las coordenadas mm predichas.
  6. Pulsa 'r' para reiniciar los clics.
  7. Pulsa 'q' o ESC para salir.

FRAME DE REFERENCIA:
  Todas las coordenadas en ROBOT_PTS deben estar en el frame GLOBAL (wobj0).
  En RobotStudio: selecciona wobj0 como frame activo al hacer jog y anota X, Y.
  La conversión a cube_storage la hace ClienteGoFa_imagen.py automáticamente
  restando el origen de cube_storage en wobj0: x=-705, y=35.
"""

import cv2
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURACIÓN: rellena ROBOT_PTS con las coordenadas de cada marca física
#  en el frame GLOBAL (wobj0), leídas en RobotStudio con wobj0 activo.
#
#  IMPORTANTE: necesitas al menos 4 puntos, no colineales (no todos en la
#  misma línea). Se recomienda 6 puntos para mayor precisión.
# ─────────────────────────────────────────────────────────────────────────────
ROBOT_PTS = [
    ( 962.39,  225.96),   # punto 1
    ( 741.32,  223.13),   # punto 2
    ( 718.63,  408.32),   # punto 3
    ( 899.91,  454.02),   # punto 4
    (   851.5,272.88),   # punto 5 — rellenar con jog en laboratorio
    (   786.91,319.71),   # punto 6 — rellenar con jog en laboratorio
]

# ─────────────────────────────────────────────────────────────────────────────
#  FUENTE DE IMAGEN
#  USAR_CAMARA = False → imagen estática (para calibrar desde casa)
#  USAR_CAMARA = True  → cámara en vivo (recomendado en laboratorio)
# ─────────────────────────────────────────────────────────────────────────────
USAR_CAMARA = False

BASE_DIR = Path(__file__).parent
IMAGEN_ESTATICA = BASE_DIR / "images" / "escenario1_coins.jpg"
OUTPUT_FILE = BASE_DIR / "homography.json"

# ─────────────────────────────────────────────────────────────────────────────
#  Estado de la aplicación
# ─────────────────────────────────────────────────────────────────────────────
pixel_pts = []       # lista de [px, py] registrados por clics
H_actual = None      # matriz de homografía calculada
modo_verificacion = False


def calcular_homografia(pix_pts, rob_pts):
    """
    Calcula la transformación píxel→mm.
    - 2-3 puntos: similitud (escala + rotación + traslación), válida si la cámara
      está razonablemente perpendicular a la mesa.
    - 4+ puntos: homografía completa con RANSAC (corrige perspectiva).
    Devuelve (H 3×3, rms_mm) o (None, inf) si falla.
    """
    src = np.array(pix_pts, dtype=np.float32)
    dst = np.array(rob_pts, dtype=np.float32)

    if len(pix_pts) < 4:
        M, _ = cv2.estimateAffinePartial2D(src, dst)
        if M is None:
            return None, float("inf")
        H = np.vstack([M, [0.0, 0.0, 1.0]])
    else:
        H, mask = cv2.findHomography(src, dst, cv2.RANSAC, ransacReprojThreshold=8.0)
    if H is None:
        return None, float("inf")

    errores = []
    for (px, py), (rx, ry) in zip(pix_pts, rob_pts):
        pred = cv2.perspectiveTransform(
            np.array([[[px, py]]], dtype=np.float32), H)[0][0]
        errores.append(float(np.linalg.norm(pred - np.array([rx, ry]))))

    rms = float(np.sqrt(np.mean(np.array(errores) ** 2)))
    return H, rms


def guardar_json(H, pix_pts, rob_pts, ruta):
    data = {
        "H": H.tolist(),
        "pixel_pts": [[int(p[0]), int(p[1])] for p in pix_pts],
        "robot_pts": [[float(r[0]), float(r[1])] for r in rob_pts],
        "frame_referencia": "wobj0",
        "fecha": datetime.now().isoformat(),
    }
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] Homografía guardada en {ruta}")


def predecir_mm(px, py, H):
    pt = np.array([[[px, py]]], dtype=np.float32)
    resultado = cv2.perspectiveTransform(pt, H)[0][0]
    return float(resultado[0]), float(resultado[1])


def dibujar_interfaz(img, pix_pts, rob_pts, H, modo_verif):
    """Dibuja anotaciones sobre la imagen base."""
    out = img.copy()
    n_esperados = len(rob_pts)
    n_registrados = len(pix_pts)

    # Puntos ya registrados
    for i, (px, py) in enumerate(pix_pts):
        cv2.circle(out, (int(px), int(py)), 6, (0, 255, 0), -1)
        cv2.putText(out, str(i + 1), (int(px) + 8, int(py) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)

    # Instrucción principal
    if modo_verif and H is not None:
        texto = "VERIFICACION: haz clic en cualquier punto | 'v' para salir"
        color_texto = (0, 200, 255)
    elif n_registrados < n_esperados:
        x_r, y_r = rob_pts[n_registrados]
        texto = (f"Clic en punto {n_registrados + 1}/{n_esperados}:  "
                 f"robot ({x_r:.1f}, {y_r:.1f}) mm")
        color_texto = (255, 255, 255)
    elif H is None:
        texto = f"Todos los puntos registrados. Pulsa 'c' para calcular."
        color_texto = (0, 255, 255)
    else:
        texto = "Homografia lista. 'v'=verificar  'r'=reiniciar  'q'=salir"
        color_texto = (0, 255, 0)

    # Fondo semitransparente para el texto
    overlay = out.copy()
    cv2.rectangle(overlay, (0, 0), (640, 30), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, out, 0.5, 0, out)
    cv2.putText(out, texto, (5, 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.52, color_texto, 1, cv2.LINE_AA)

    return out


def on_mouse(event, x, y, flags, param):
    global pixel_pts, H_actual, modo_verificacion
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    if modo_verificacion:
        if H_actual is not None:
            x_mm, y_mm = predecir_mm(x, y, H_actual)
            print(f"  [VERIF] píxel ({x}, {y})  →  robot ({x_mm:.1f}, {y_mm:.1f}) mm")
        return

    if len(pixel_pts) < len(ROBOT_PTS):
        pixel_pts.append([x, y])
        idx = len(pixel_pts)
        rx, ry = ROBOT_PTS[idx - 1]
        print(f"  Punto {idx}: píxel ({x}, {y})  ←→  robot ({rx:.1f}, {ry:.1f}) mm")


def main():
    global pixel_pts, H_actual, modo_verificacion

    # Fuente de imagen
    if USAR_CAMARA:
        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ret, img_base = cap.read()
        if not ret:
            print("[ERROR] No se pudo capturar frame de la cámara.")
            return
        cap.release()
    else:
        img_base = cv2.imread(str(IMAGEN_ESTATICA))
        if img_base is None:
            print(f"[ERROR] No se encontró: {IMAGEN_ESTATICA}")
            return
        img_base = cv2.resize(img_base, (640, 480))

    print("=" * 60)
    print("CALIBRACIÓN DE HOMOGRAFÍA")
    print("=" * 60)
    print(f"Puntos a registrar: {len(ROBOT_PTS)}")
    for i, (rx, ry) in enumerate(ROBOT_PTS, 1):
        print(f"  Punto {i:2d}: robot ({rx:.1f}, {ry:.1f}) mm")
    print()
    print("Controles:")
    print("  Clic izquierdo → registrar punto")
    print("  c → calcular homografía")
    print("  v → modo verificación (clic libre → predice mm)")
    print("  r → reiniciar puntos")
    print("  q / ESC → salir")
    print("=" * 60)

    cv2.namedWindow("Calibración Homografía")
    cv2.setMouseCallback("Calibración Homografía", on_mouse)

    while True:
        frame_mostrado = dibujar_interfaz(
            img_base, pixel_pts, ROBOT_PTS, H_actual, modo_verificacion)
        cv2.imshow("Calibración Homografía", frame_mostrado)

        key = cv2.waitKey(50) & 0xFF

        if key in (ord('q'), 27):  # q o ESC
            break

        elif key == ord('r'):
            pixel_pts = []
            H_actual = None
            modo_verificacion = False
            print("[RESET] Puntos reiniciados.")

        elif key == ord('c'):
            if len(pixel_pts) < 2:
                print(f"[AVISO] Se necesitan al menos 2 puntos. "
                      f"Tienes {len(pixel_pts)}.")
            elif len(pixel_pts) < len(ROBOT_PTS):
                print(f"[AVISO] Solo tienes {len(pixel_pts)} de {len(ROBOT_PTS)} "
                      f"puntos. Puedes calcular igualmente (≥4).")
                usados_px = pixel_pts
                usados_rb = list(ROBOT_PTS[:len(pixel_pts)])
                H_actual, rms = calcular_homografia(usados_px, usados_rb)
                _mostrar_resultado(H_actual, rms, usados_px, usados_rb)
            else:
                H_actual, rms = calcular_homografia(pixel_pts, list(ROBOT_PTS))
                _mostrar_resultado(H_actual, rms, pixel_pts, list(ROBOT_PTS))

        elif key == ord('v'):
            if H_actual is None:
                print("[AVISO] Primero calcula la homografía con 'c'.")
            else:
                modo_verificacion = not modo_verificacion
                estado = "ACTIVADO" if modo_verificacion else "DESACTIVADO"
                print(f"[VERIF] Modo verificación {estado}.")


    cv2.destroyAllWindows()


def _mostrar_resultado(H, rms, pix_pts, rob_pts):
    global H_actual
    if H is None:
        print("[ERROR] No se pudo calcular la homografía. Revisa los puntos.")
        return

    print()
    print("─" * 50)
    print(f"  Error RMS: {rms:.2f} mm", end="  ")
    if rms < 5:
        print("✓ Excelente")
    elif rms < 15:
        print("~ Aceptable")
    else:
        print("✗ Revisar puntos")
    print()

    for i, ((px, py), (rx, ry)) in enumerate(zip(pix_pts, rob_pts), 1):
        pred = cv2.perspectiveTransform(
            np.array([[[px, py]]], dtype=np.float32), H)[0][0]
        err = float(np.linalg.norm(pred - np.array([rx, ry])))
        print(f"  Pto {i:2d}: píxel({px:3d},{py:3d}) → pred({pred[0]:6.1f},{pred[1]:6.1f}) "
              f"real({rx:6.1f},{ry:6.1f})  err={err:.1f}mm")

    print("─" * 50)
    guardar_json(H, pix_pts, rob_pts, OUTPUT_FILE)
    H_actual = H


if __name__ == "__main__":
    main()
