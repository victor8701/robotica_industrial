# Puesta en marcha — 5 mayo

## Verificación de la Z de recogida

Python solo envía **X e Y** al robot. La coordenada **Z** del punto de recogida (`ptoCamara`) no viene de la cámara: queda fijada por el valor `ptoAux.trans.z`, que actualmente es **100 mm** en `wobj0`.

Para verificar y ajustar:

1. Pon el robot en modo **Manual** en RobotStudio
2. Mueve el TCP manualmente hasta tocar la superficie de un cubo en el área de trabajo
3. Anota el valor **Z** que muestra RobotStudio con `wobj0` activo
4. Si ese valor difiere de 100 mm, actualiza `ptoAux.trans.z` en RobotStudio con el valor correcto

**Referencia:** `ptoPick.trans.z = 56 mm` (posición de depósito fija, ya verificada).

---

## Velocidades a ajustar en el laboratorio

Las velocidades actuales en `VisionPickPlace.modx` son conservadoras para un primer test, pero conviene verificarlas antes de soltar el robot a velocidad normal.

| Movimiento | Variable RAPID | Valor actual | Rango a probar |
|---|---|---|---|
| Ir/volver a `ptoReposo` | `v1000` / `v800` | 1000 / 800 mm/s | 200–500 |
| `MoveJ` a aproximación sobre cubo | `v800` | 800 mm/s | 100–300 — **este es el más crítico**: `ptoCamara` viene de la cámara y puede ser inesperado |
| Bajar al cubo (`MoveL`) | `v100` | 100 mm/s | dejar en 100 |
| Subir tras coger | `v400` | 400 mm/s | 200–400 |
| `MoveJ` a aproximación sobre depósito | `v800` | 800 mm/s | 200–400 |
| Bajar al depósito (`MoveL`) | `v100` | 100 mm/s | dejar en 100 |

**El movimiento más arriesgado** es el `MoveJ Offs(ptoCamara,0,0,100)`: va a una posición variable calculada por la cámara. Si hay una detección errónea, el robot se dirige a esa posición inesperada a la velocidad configurada. Empieza con v200 y sube solo cuando compruebes que las detecciones son estables.

> El GoFa (Omnicore) tiene limitación de velocidad por seguridad colaborativa, pero no confíes en eso como única barrera en las primeras pruebas.
