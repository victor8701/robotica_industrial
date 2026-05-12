MODULE HMIData
    ! Variables compartidas entre la WebApp HMI y RAPID.
    ! La WebApp escribe selectedColor, startPick y piecesToPick.
    ! RAPID escribe robotBusy y piecesPickedCount.

    PERS num  selectedColor     := 0;  ! 0=ninguno 1=amarillo 2=azul 3=rojo 4=verde
    PERS bool startPick         := FALSE;  ! TRUE = iniciar; RAPID lo resetea a FALSE tras leerlo
    PERS bool robotBusy         := FALSE;  ! TRUE mientras robot ejecuta tarea
    PERS num  piecesPickedCount := 0;  ! piezas recogidas en total
    PERS num  piecesToPick      := 1;  ! cantidad solicitada desde HMI
    PERS bool usePLC            := FALSE;  ! TRUE = escuchar PLC; FALSE = escuchar HMI (webapp)

ENDMODULE
