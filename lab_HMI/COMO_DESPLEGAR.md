# Cómo poner en marcha la WebApp HMI

## Paso 1 — Copiar las librerías del SDK (solo una vez)

Desde `Downloads/OmniCoreAppSDK-1.6.0/OmniCoreAppSDK-1.6.0/libraries/`:

- Copia **toda** la carpeta `fp-components/` → `lab_HMI/webapp/fp-components/`
- Copia **toda** la carpeta `rws-api/` → `lab_HMI/webapp/rws-api/`
- Copia `defaulticon.png` desde cualquier ejemplo del SDK → `lab_HMI/webapp/defaulticon.png`

## Paso 2 — Cargar el módulo RAPID

En RobotStudio → pestaña Controller → clic derecho sobre la tarea `T_ROB1` → **Load module** → selecciona `lab_HMI/RAPID/HMIData.mod`.

## Paso 3 — Cargar la configuración EIO (si aún no está)

En RobotStudio → Controller → **Load parameters** → selecciona el `EIO.cfg` del controlador real.  
Elige **"Load parameters and replace duplicates"**.

## Paso 4 — Copiar la webapp al controlador

Copia la carpeta `lab_HMI/webapp/` completa a la ruta del controlador:

```
HOME/WebApps/PickPlaceHMI/
```

La estructura debe quedar:
```
HOME/WebApps/PickPlaceHMI/
  appinfo.xml
  index.html
  app.js
  app.css
  defaulticon.png
  fp-components/
  rws-api/
```

## Paso 5 — Reiniciar y verificar

1. Reinicia el controlador (o solo el FlexPendant si el controlador lo permite)
2. En el FlexPendant aparecerá la app **"Pick & Place HMI"** en el menú de aplicaciones
3. Si sale error "Error al conectar con RAPID": comprueba que `HMIData.mod` está cargado y el módulo se llama exactamente `HMIData`

## Integrar con el programa de pick&place

En `VisionPickPlace.modx` (o donde esté el main), añade la lógica del comentario en `HMIData.mod`:

```rapid
WaitUntil startPick = TRUE;
startPick := FALSE;
robotBusy := TRUE;
! ... lógica de recogida según selectedColor ...
piecesPickedCount := piecesPickedCount + 1;
robotBusy := FALSE;
```
