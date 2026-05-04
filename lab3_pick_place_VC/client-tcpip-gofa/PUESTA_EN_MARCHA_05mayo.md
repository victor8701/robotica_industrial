# Puesta en marcha — 5 mayo

## Estado actual (verificado en controlador virtual)

| Elemento | Estado |
|---|---|
| Webapp HMI desplegada en VC | OK |
| HMIData.mod cargado (PERS) | OK — amarillo seleccionado por defecto, feedback visual funciona |
| VisionPickPlace.modx con integracion HMI | OK — startPick, robotBusy, piecesToPick, piecesPickedCount |
| Archivos RAPID en ASCII puro | OK — sin acentos, sin problemas de codificacion ISO-8859-1 |
| Calibracion homografia offline | Pendiente — Revisar |

---

## Problema sesion anterior: robot no llegaba a los cubos

En la sesion del 28 de abril el robot iba a posiciones con coordenadas numericament razonables pero no coincidian con la posicion real de los cubos.

### Candidatos (de mas a menos probable)

**A. Workobject incorrecto al medir ROBOT_PTS**  
Si al hacer jog para medir los puntos de calibracion tenias activo `Workobject_1` en lugar de `wobj0`, los valores anotados estan en el frame de Workobject_1. Su origen en wobj0 es (329 mm, 70 mm, 0). RAPID mueve con `\WObj:=wobj0`, asi que hay un offset constante de ~329 mm en X y ~70 mm en Y entre donde va el robot y donde deberia ir.

**Test rapido**: jog hasta un cubo conocido y anota la posicion en wobj0 y en Workobject_1. Luego abre `calibrar_homografia.py` en modo verificacion (`v`) y haz clic encima de ese cubo. Las coordenadas predichas deben coincidir con **wobj0**, no con Workobject_1.

**B. Ejes X/Y invertidos entre camara y robot**  
Si la camara esta montada con una rotacion de 90 grados respecto al frame del robot, el eje X de la camara puede corresponder al Y del robot y viceversa. El robot va a una posicion con valores numericos parecidos pero transpuestos.

**Test**: en modo verificacion de `calibrar_homografia.py`, haz clic en un punto que sabes que esta a mas X que otro (mas a la derecha en la camara) y comprueba que la coordenada X predicha tambien sube. Si sube la Y, los ejes estan intercambiados.

**C. homography.json no generado o con mal RMS**  
Sin el fichero, Python envia pixeles como mm. El script avisa:
```
[AVISO] homography.json no encontrado. Las coordenadas enviadas al robot seran en pixeles (incorrecto).
```

**D. Otros**
- `formatear_coordenadas()` hace clamp a [0, 999]: si el cubo esta a X > 999 mm en wobj0, la coordenada se trunca.
- La Z de recogida (`ptoAux.trans.z = 100 mm`) puede no coincidir con la altura real de los cubos.

---

## Verificacion antes de arrancar (checklist)

### 0. Confirmar el frame de referencia antes de medir puntos

En RobotStudio, antes de hacer jog para medir cualquier punto de calibracion:  
**Robotics → Coordinate system → selecciona `wobj0`** (no Workobject_1, no Tool).

Si tienes dudas de con que frame se midieron los ROBOT_PTS actuales: jog hasta un cubo, anota la posicion en wobj0 y en Workobject_1, y compara con los valores de `ROBOT_PTS`. El frame que coincida es el que se uso.

### 1. Comprobar que la homografia es valida

```bash
python calibrar_homografia.py   # USAR_CAMARA = False para verificar en casa
```

Cuando pida los 6 puntos, haz clic sobre las marcas fisicas en el mismo orden que `ROBOT_PTS`. Tras pulsar `c`:
- RMS < 5 mm → homografia correcta, puedes continuar
- RMS 5-15 mm → aceptable para primer test, pero repite con mas cuidado
- RMS > 15 mm → repite la calibracion; algún punto estaba mal clicado

Luego pulsa `v` (modo verificacion) y haz clic encima de donde estan los cubos en la imagen. Las coordenadas mm predichas deben coincidir con lo que marca RobotStudio al hacer jog al mismo punto fisico.

### 2. Confirmar que homography.json existe antes de arrancar Python

El script avisa si no lo encuentra:
```
[AVISO] homography.json no encontrado. Las coordenadas enviadas al robot seran en pixeles (incorrecto).
```
Si ves este aviso, **no arranques con el robot** hasta calibrar.

### 3. Verificar la Z de recogida antes del primer ciclo completo

En Modo Manual: jog el TCP hasta tocar la superficie de un cubo con la herramienta Magnet.  
Anota la Z en RobotStudio (frame wobj0). Si difiere de 100 mm → modifica `ptoAux.trans.z` en `RAPID/CalibData.modx` o directamente desde RobotStudio → RAPID Data.

Referencia: `ptoPick.trans.z = 56 mm` (punto de deposito, ya verificado en sesion anterior).

### 4. Test de coordenadas sin mover el robot

Con Python conectado y el programa RAPID corriendo en el WHILE, fuerza una pausa antes de `MoveJ` en RobotStudio (breakpoint o Stop manual). Observa el valor de `ptoCamara.trans.x` y `.trans.y` en RAPID Data. Deben estar en el rango esperado del workspace (aprox X=750-1000, Y=150-550 en wobj0). Si ves valores como X=320, Y=240 → la homografia no se esta aplicando.

### 5. Si el robot da error de alcance al moverse

1. Comprueba que `ptoCamara` tiene coordenadas razonables (paso 4).
2. Comprueba que la herramienta activa es **Magnet** (no Pen ni ninguna otra).
3. Mueve el robot manualmente cerca de `ptoReposo` antes de dar Run — el primer MoveJ lo lleva ahi y desde ahi alcanza el workspace de cubos.
4. Si el error persiste con coordenadas correctas: ajusta `ptoAux.trans.z` (la Z influye en el alcance).
5. Usa velocidades bajas (v200) el primer dia — si el robot para por alcance con v200 ya lo ves venir con tiempo.

---

## Secuencia de arranque en el laboratorio

### 1. Desplegar webapp al robot real

Copiar el contenido de `lab_HMI/webapp/` a `HOME\WebApps\PickPlaceHMI\` en el robot real:
- Metodo: RobotStudio conectado al robot → File Transfer
- Archivos: `index.html`, `app.js`, `app.css`, `appinfo.xml`, `defaulticon.png`, carpetas `fp-components/` y `rws-api/`

### 2. Cargar modulos RAPID en el robot real

Controller → RAPID → T_ROB1 → clic derecho → **Load Module** (en este orden):

1. `RAPID/HMIData.mod`
2. `RAPID/CalibData.modx`
3. `RAPID/VisionPickPlace.modx`

> HMIData debe cargarse antes que VisionPickPlace — este ultimo usa sus variables.

### 3. Reiniciar FlexPendant

FlexPendant → ABB Menu → Restart → la app "Pick & Place HMI" debe aparecer en Apps.

### 4. Arrancar el programa RAPID

- PP to Main → Run
- El programa queda bloqueado en `SocketAccept` esperando al cliente Python

### 5. Arrancar el cliente Python

```bash
python ClienteGoFa_imagen.py   # CONECTAR_ROBOT=True, con homography.json valido
```

El robot acepta la conexion y entra en el bucle WHILE. A partir de aqui el HMI esta activo.

### 6. Flujo normal de uso

1. Camara detecta un cubo → Python envia coordenadas continuas
2. En el HMI: color ya seleccionado (amarillo por defecto), ajusta cantidad si hace falta
3. Pulsa **INICIAR** → dialogo de confirmacion → **OK**
4. RAPID comprueba `startPick` en el siguiente ciclo TCP → ejecuta `recogerPieza`
5. HMI muestra **OCUPADO** (naranja) durante la recogida
6. Contador "Piezas recogidas" sube al terminar → HMI vuelve a **LIBRE**

---

## Verificacion de la Z de recogida

Python solo envia **X e Y**. La **Z** de `ptoCamara` queda fijada por `ptoAux.trans.z` (actualmente **100 mm** en wobj0).

1. Modo Manual → jog el TCP hasta tocar la superficie de un cubo
2. Anota la Z que muestra RobotStudio (wobj0)
3. Si difiere de 100 mm → modifica `ptoAux.trans.z` en CalibData.modx o directamente en RobotStudio

**Referencia:** `ptoPick.trans.z = 56 mm` (punto de deposito, ya verificado).

---

## Velocidades a ajustar

| Movimiento | Valor actual | Recomendacion primer test |
|---|---|---|
| Ir/volver a `ptoReposo` | v1000 / v800 | v300 |
| `MoveJ` aproximacion sobre cubo | v800 | **v200** — mas critico: posicion variable de camara |
| `MoveL` bajar al cubo | v100 | mantener |
| Subir tras coger | v400 | v200 |
| `MoveJ` aproximacion sobre deposito | v800 | v300 |
| `MoveL` bajar al deposito | v100 | mantener |

> El movimiento mas arriesgado es `MoveJ Offs(ptoCamara,0,0,100)`: va a una posicion calculada por la camara. Empieza en v200 y sube solo cuando las detecciones sean estables.

---

## Calibracion homografia

Los puntos 1 y 2 de `ROBOT_PTS` en `calibrar_homografia.py` estan verificados con medidas reales del lab anterior. Los puntos 3-6 tienen valores introducidos pero **pendientes de confirmar** con jog del robot.

**Antes de usar el robot en esta sesion:**

1. Para cada punto 3-6: jog el TCP hasta la marca fisica correspondiente, anota X e Y en wobj0 y actualiza `ROBOT_PTS` en `calibrar_homografia.py`.
2. Ejecuta la calibracion:

```bash
python calibrar_homografia.py   # USAR_CAMARA = True en el lab, False para test con imagen estatica
```

3. Cuando pida los puntos, haz clic sobre las marcas fisicas en orden.
4. Pulsa `c` → comprueba RMS. Objetivo: < 5 mm. Si > 15 mm, alguna marca estaba mal clicada — pulsa `r` y repite.
5. Pulsa `v` y haz clic donde estan los cubos para verificar que las coordenadas predichas coinciden con lo que marca RobotStudio.
6. El script guarda `homography.json` automaticamente — sin el, Python envia pixeles como mm y el robot va a posiciones incorrectas.
