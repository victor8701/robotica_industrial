import cv2
import numpy as np
import socket
import time
import json
mi_socket = socket.socket()
mi_socket.connect(("192.168.125.1" , 1025))
respuesta = mi_socket.recv(1024)
print(respuesta)
mi_socket.sendall('Server connected'.encode())

def dibujar(mask,color):
  contornos,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)
  for c in contornos:
    area = cv2.contourArea(c)
    if area > 2000:
      M = cv2.moments(c)
      if (M["m00"]==0): M["m00"]=1
      x = int(M["m10"]/M["m00"])
      y = int(M['m01']/M['m00'])
      
      # Convertir píxeles a milímetros reales usando la calibración
      pt = np.array([[[x, y]]], dtype=np.float32)
      res = cv2.perspectiveTransform(pt, H_global)[0][0]
      x_mm, y_mm = float(res[0]), float(res[1])
      
      # Ignorar la zona de la izquierda (donde el robot deja los cubos)
      if x_mm < 500:
          continue
          
      nuevoContorno = cv2.convexHull(c)
      cv2.circle(frame,(x,y),7,(0,255,0),-1)
      
      # Formatear a XXXYYY
      x_str = str(max(0, min(999, int(round(x_mm))))).zfill(3)
      y_str = str(max(0, min(999, int(round(y_mm))))).zfill(3)
      
      label = f'{x_str},{y_str}mm'
      cv2.putText(frame,label,(x+10,y), font, 0.65,(0,255,0),1,cv2.LINE_AA)
      
      cv2.drawContours(frame, [nuevoContorno], 0, color, 3)
      
      coordXY = x_str + y_str
      mi_socket.sendall(coordXY.encode())
      time.sleep(1)
      print("Coordenadas enviadas: " + coordXY)

with open("homography.json", "r", encoding="utf-8") as f:
    H_global = np.array(json.load(f)["H"], dtype=np.float64)

cap = cv2.VideoCapture(2)
azulBajo = np.array([90, 120, 80],np.uint8)
azulAlto = np.array([130, 255, 255],np.uint8)
amarilloBajo = np.array([20, 120, 80],np.uint8)
amarilloAlto = np.array([40, 255, 255],np.uint8)
redBajo1 = np.array([0, 120, 80],np.uint8)
redAlto1 = np.array([8, 255, 255],np.uint8)
redBajo2 = np.array([170, 120, 80],np.uint8)
redAlto2 = np.array([179, 255, 255],np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    ret,frame = cap.read()

    if ret == True:
        frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        maskAzul = cv2.inRange(frameHSV,azulBajo,azulAlto)
        maskAmarillo = cv2.inRange(frameHSV,amarilloBajo,amarilloAlto)
        maskRed1 = cv2.inRange(frameHSV,redBajo1,redAlto1)
        maskRed2 = cv2.inRange(frameHSV,redBajo2,redAlto2)
        maskRed = cv2.add(maskRed1,maskRed2)
        dibujar(maskAzul,(255,0,0))
        dibujar(maskAmarillo,(0,255,255))
        dibujar(maskRed,(0,0,255))
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            mi_socket.close()
            break
cap.release()
cv2.destroyAllWindows()