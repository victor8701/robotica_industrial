# Puesta en marcha — 5 mayo

## Estado actual (verificado en controlador virtual)

| Elemento | Estado |
|---|---|
| Webapp HMI desplegada en VC | OK |
| HMIData.mod cargado (PERS) | OK — amarillo seleccionado por defecto, feedback visual funciona |
| VisionPickPlace.modx con integracion HMI | OK — startPick, robotBusy, piecesToPick, piecesPickedCount |
| Archivos RAPID en ASCII puro | OK — sin acentos, sin problemas de codificacion ISO-8859-1 |
| Calibracion homografia offline | Pendiente — rellenar ROBOT_PTS 5 y 6 con medidas reales |

---

## Secuencia de arranque en el laboratorio

### 1. Desplegar webapp al robot real

Copiar el contenido de `lab_HMI/webapp/` a `HOME\WebApps\PickPlaceHMI\` en el robot real:
- Metodo: RobotStudio conectado al robot → File Transfer
- Archivos: `index.html`, `app.js`, `app.css`, `appinfo.xml`, `defaulticon.png`, carpetas `fp-components/` y `rws-api/`

### 2. Cargar modulos RAPID en el robot real

Controller → RAPID → T_ROB1 → clic derecho → **Load Module** (en este orden):

1. `lab_HMI/RAPID/HMIData.mod`
2. `lab3_pick_place_VC/client-tcpip-gofa/RAPID/CalibData.modx`
3. `lab3_pick_place_VC/client-tcpip-gofa/RAPID/VisionPickPlace.modx`

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

## Calibracion homografia (pendiente)

Rellenar en `calibrar_homografia.py` los puntos 5 y 6 de `ROBOT_PTS` con medidas reales tomadas con cinta metrica o jog del robot (coordenadas wobj0).

```bash
python calibrar_homografia.py   # USAR_CAMARA = False para test con imagen estatica
```

RMS objetivo: < 5 mm. Si > 15 mm, repetir calibracion.
