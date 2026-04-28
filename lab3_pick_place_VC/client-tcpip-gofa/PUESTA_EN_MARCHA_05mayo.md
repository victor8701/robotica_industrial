# Puesta en marcha — 5 mayo

## Verificación de la Z de recogida

Python solo envía **X e Y** al robot. La coordenada **Z** del punto de recogida (`ptoCamara`) no viene de la cámara: queda fijada por el valor `ptoAux.trans.z`, que actualmente es **100 mm** en `wobj0`.

Para verificar y ajustar:

1. Pon el robot en modo **Manual** en RobotStudio
2. Mueve el TCP manualmente hasta tocar la superficie de un cubo en el área de trabajo
3. Anota el valor **Z** que muestra RobotStudio con `wobj0` activo
4. Si ese valor difiere de 100 mm, actualiza `ptoAux.trans.z` en RobotStudio con el valor correcto

**Referencia:** `ptoPick.trans.z = 56 mm` (posición de depósito fija, ya verificada).
