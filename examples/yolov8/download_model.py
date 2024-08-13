import requests

def download_model():
    url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt'
    r = requests.get(url)
    with open('yolov8s.pt', 'wb') as f:
        f.write(r.content)
        print('Model downloaded as yolov8s.pt')

download_model()
