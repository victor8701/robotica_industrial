# Guía de puesta en marcha en el laboratorio

## Antes de empezar

- Tener el portátil con el repositorio actualizado
- RobotStudio abierto y conectado al controlador Omnicore
- Cámara conectada al portátil (índice 1)
- Red local: portátil en `192.168.1.x`, robot en `192.168.1.89`

---

## Sistema de coordenadas — qué significa cada número

Cuando `ClienteGoFa_imagen.py` muestra el overlay **`320,240px → 185,310mm`** sobre un cubo, los valores en mm son coordenadas en el frame **`Workobject_1`** de RobotStudio, no en píxeles ni en ninguna esquina de la imagen.

```
wobj0 (frame base del robot)
  └─ Workobject_1  ←── origen aquí (punto físico definido en RobotStudio)
       ├── X_mm: distancia en mm a lo largo del eje X de Workobject_1
       └── Y_mm: distancia en mm a lo largo del eje Y de Workobject_1
```

**Dónde está el origen (0, 0):**  
El punto que en RobotStudio tiene coordenadas `(0, 0)` cuando `Workobject_1` es el frame activo. Normalmente es una esquina de la mesa o un punto de referencia que se fijó al crear el workobject. **No es la esquina de la imagen de la cámara.**

**Por qué importa:**  
RAPID recibe el string `"XXXYYYY"` y lo interpreta directamente como `(X mm, Y mm)` en `Workobject_1`. Si se enviaran píxeles (0–640, 0–480) en lugar de mm, el robot iría a posiciones completamente erróneas. La homografía hace exactamente esa conversión.

**wobj0 vs Workobject_1:**  
`Workobject_1` está desplazado aproximadamente `[329 mm en X, 70 mm en Y]` respecto a `wobj0` (el frame del robot). Por eso en el Paso 2 hay que hacer jog seleccionando `Workobject_1` como frame, no `wobj0`.

---

## Paso 1 — Fijar la cámara

Monta la cámara en su posición definitiva sobre la mesa. **Una vez calibrada, no moverla.**
Si se mueve accidentalmente, repite desde el Paso 2.

---

## Paso 2 — Obtener las coordenadas reales para calibrar_homografia.py

**Qué puntos elegir:**  
Cualquier punto físico que la cámara pueda ver sirve. No tienen por qué ser esquinas de la mesa.  
Lo único que importa es que estén **bien repartidos** por toda el área visible (no todos juntos ni en línea recta) y que puedas identificarlos físicamente para que el robot llegue exactamente ahí.

Método recomendado: pega **4 trozos de cinta adhesiva** en la mesa, bien separados entre sí:

```
vista de la cámara:

  [cinta 1]─────────────[cinta 4]
      │                     │
      │                     │
  [cinta 2]─────────────[cinta 3]
```

Con 4 puntos la homografía se calcula exactamente. Si quieres detectar errores de clic añade 2 más en cualquier posición intermedia.

En RobotStudio (modo Manual / Jog):

1. Selecciona **`Workobject_1`** como frame de referencia en el FlexPendant  
   *(si usas wobj0 por error, los valores estarán desplazados ~329 mm en X y ~70 mm en Y)*
2. Mueve el TCP manualmente hasta cada trozo de cinta
3. Anota los valores **X, Y** que muestra RobotStudio para cada uno

Abre [calibrar_homografia.py](calibrar_homografia.py) y sustituye `ROBOT_PTS` con los valores anotados, **en el orden en que vas a hacer clic en la imagen**:

```python
ROBOT_PTS = [
    (X1, Y1),   # descripción del punto 1
    (X2, Y2),   # descripción del punto 2
    ...
]
```

Cambia también `USAR_CAMARA = True` para usar la imagen en vivo.

---

## Paso 3 — Calibrar la homografía

```bash
python calibrar_homografia.py
```

1. Se abre la ventana con la imagen de la cámara en vivo
2. Haz clic sobre cada punto físico **en el mismo orden que en `ROBOT_PTS`**  
   (el script te indica en pantalla qué punto toca a continuación)
3. Cuando hayas registrado todos los puntos, pulsa **`c`**
4. Revisa el error RMS en la consola:
   - **< 5 mm** → correcto, continúa
   - **5–15 mm** → aceptable, mira qué punto tiene más error y repítelo con `r`
   - **> 15 mm** → algo está mal (orden de clics incorrecto, o valor de robot equivocado), repite
5. Si el RMS es bueno, pulsa **`v`** y haz clic sobre un punto cuya coordenada conozcas para verificar la predicción
6. Al salir se habrá generado `homography.json` automáticamente al pulsar `c`

---

## Paso 4 — Verificar offline antes de conectar el robot

Abre [ClienteGoFa_imagen.py](ClienteGoFa_imagen.py) y comprueba que:

```python
USAR_CAMARA = True
CONECTAR_ROBOT = False   # aún sin robot
```

Ejecuta:

```bash
python ClienteGoFa_imagen.py
```

- En la ventana de vídeo debes ver el overlay **`px,py → Xmm,Ymm`** sobre los cubos detectados
- Comprueba que las coordenadas mm son coherentes con el espacio de trabajo  
  (valores dentro del rango de `ROBOT_PTS`, no negativos ni absurdos)
- Si los valores son incorrectos, repite el Paso 3

---

## Paso 5 — Conectar el robot

En [ClienteGoFa_imagen.py](ClienteGoFa_imagen.py):

```python
USAR_CAMARA = True
CONECTAR_ROBOT = True
```

Asegúrate de que en RobotStudio está corriendo `VisionPickPlace.modx` (servidor TCP/IP activo).

```bash
python ClienteGoFa_imagen.py
```

- El robot debe conectarse e ir a posición de reposo
- Coloca un cubo amarillo en el área de trabajo
- El robot debería desplazarse a las coordenadas del cubo y ejecutar el pick

---

## Paso 6 — Test de robustez

Mueve el cubo a al menos 3 posiciones distintas del área de trabajo y verifica que el robot alcanza cada una correctamente. Si alguna posición falla, revisa el RMS de calibración.

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `homography.json no encontrado` | No se ejecutó el Paso 3 | Ejecutar `calibrar_homografia.py` |
| Coordenadas mm negativas o > 2000 | Cámara movida o puntos de calibración mal | Repetir Paso 2 y 3 |
| El robot va a una posición incorrecta | `ROBOT_PTS` medido en wobj0 en vez de Workobject_1 | Restar `[329.172, 70.377]` mm a todos los puntos y recalibrar |
| RMS > 15 mm | Clics en orden incorrecto o punto equivocado | Pulsar `r` y repetir los clics |
| No detecta cubos amarillos | Iluminación diferente al laboratorio | Ejecutar `ajuste_parametros_cubos_amarillos.py` y guardar nuevo config |
