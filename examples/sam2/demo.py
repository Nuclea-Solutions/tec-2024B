from ultralytics import SAM
import cv2
import os
import time

# Cargar modelo (y descargar en caso que no este presente)
model = SAM("sam_b.pt")

# Ubicacion de la imagen
video_path = os.path.join('..', '..', 'assets', 'aerial-drone.mp4')

cap = cv2.VideoCapture(video_path)

# revisamos si el video se abrio correctamente
while cap.isOpened():
    # leemos un frame del video
    ret, frame = cap.read()

    # verificamos si el frame se leyo correctamente
    if not ret:
        break

    # results = model(frame)
    results = model(frame, bboxes=[100, 100, 1200, 800])

    # solo enviamos un frame por lo que solo hay un resultado
    # obtenemos el frame con los objetos detectados y ya graficados
    # con su bounding box y etiqueta
    annotated_frame = results[0].plot()

    # display results
    cv2.imshow('SAM2', annotated_frame)

    # si se presiona la tecla 'q' se cierra el video
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break