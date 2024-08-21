from ultralytics import YOLO
import socket
import logging
import cv2
import numpy as np
from threading import Thread, Event as ThreadEvent

model = YOLO('yolov8s.pt')

def clean_buffer(original_buffer):
    buffer = b''
    for b in original_buffer:
        if b == 255:
            break
        buffer += bytes([b])
    return buffer

def get_numeric_data(buffer):
    numeric_buffer = b''
    left_bytes = b''

    for b in buffer:
        if b >= 48 and b <= 57:
            numeric_buffer += bytes([b])
        else:
            left_bytes += bytes([b])

    return numeric_buffer, left_bytes

def handle_socket_client(client_socket, addr):
    logger = logging.getLogger("handle_socket_client")
    logger.info("connected to client: {}".format(addr))

    while True:
        # the payload is composed of two parts:
        # +---------------------------------+-----------------+
        # | length of bytes to be received  | image bytes     |
        # +---------------------------------+-----------------+

        # receive the length of bytes to be received
        # we assumed the number of bytes at most will be in 7 bytes
        # in practice, this number will be less than 7 bytes, probably 6
        data = client_socket.recv(7)
        if not data:
            break

        # get the numeric data from the received bytes
        # telling us how many bytes we should expect
        # the rest of the buffer is part of the image bytes
        numeric_data, initial_buffer = get_numeric_data(data)

        # convert the received bytes to integer
        data_len = int(numeric_data.decode('ascii'))
        logger.info("data_len: {}".format(data_len))

        buffer = initial_buffer
        bytes_left = data_len - len(buffer)

        while True:
            # receive the image bytes
            logger.info('bytes left: {}'.format(bytes_left))
            fragment = client_socket.recv(bytes_left)
            logger.info('read bytes: {}'.format(len(fragment)))
            if not fragment:
                break

            buffer += fragment
            if len(buffer) == data_len:
                break
            else:
                bytes_left = data_len - len(fragment)

        if len(buffer) != data_len:
            logger.error("received data length does not match the expected length")
            break

        # save the received image
        # with open('images/{}.jpg'.format(counter), 'wb') as fw:
        #     fw.write(buffer)

        nparr = np.frombuffer(buffer, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # For now, let's just display the received image
        results = model.track(img, persist=True)

        annotated_frame = results[0].plot()

        # display results
        cv2.imshow('YOLOv8 Tracking', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    client_socket.close()
    cv2.destroyAllWindows()
    logger.info("client disconnected")

def socket_server():
    logger = logging.getLogger("socket_server")

    HOST = '127.0.0.1'
    PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket.settimeout(1)

    logger.info("server listening on port: {}:{}".format(HOST, PORT))
    while not exit_socket_server_flag.is_set():
        try:
            client_socket, addr = server_socket.accept()
            Thread(target=handle_socket_client, args=(client_socket, addr)).start()
        except socket.timeout:
            continue

    logger.info("terminating socket server")
    server_socket.close()


exit_socket_server_flag = ThreadEvent()

socket_server_thread = Thread(target=socket_server)
socket_server_thread.start()

while True:
    # if user presses 'q' then exit
    if input("press 'q' to exit\n") == 'q':
        # set flag to be able to terminate the socket server
        exit_socket_server_flag.set()
        break

# join threads
# event_thread.join()
socket_server_thread.join()
