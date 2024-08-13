from ultralytics import YOLO
from os import path
import cv2

model = YOLO('yolov8s.pt')

# construir el path hacia el video de demo
video_path = path.join('..', '..', 'assets', 'aerial-drone.mp4')

# abrir el video con opencv
cap = cv2.VideoCapture(video_path)

# revisamos si el video se abrio correctamente
while cap.isOpened():
    # leemos un frame del video
    ret, frame = cap.read()

    # verificamos si el frame se leyo correctamente
    if not ret:
        break

    # detectar objetos en el frame
    results = model.track(frame, persist=True)

    # solo enviamos un frame por lo que solo hay un resultado
    # obtenemos el frame con los objetos detectados y ya graficados
    # con su bounding box y etiqueta
    annotated_frame = results[0].plot()

    # display results
    cv2.imshow('YOLOv8 Tracking', annotated_frame)

    # si se presiona la tecla 'q' se cierra el video
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

