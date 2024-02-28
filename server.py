import cv2
import time
import socket
import argparse
from yolo.YoloV8 import Yolov8s

#CMD: python3 ./server.py --sc True
video_config = 'v4l2src device=/dev/video0 ! video/x-raw, format=YUY2, width=640, height=480, framerate=30/1 ! nvvidconv ! video/x-raw(memory:NVMM) ! nvvidconv ! video/x-raw, format=BGRx !  videoconvert ! video/x-raw, format=BGR ! appsink'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Initialize IP and PORT.")
server_socket.bind(('127.0.0.8', 12345))
server_socket.listen(1)
print("Server is listening for connections...")
client_socket, client_address = server_socket.accept()
print("Connected: ", client_address)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sc', type=bool, default=False, help='Set value to endcode view camera')
    args = parser.parse_args()
    print("Check:", args)
    return args

class Server():
    def __init__(self, args) -> None:
        self.showCamera = args.sc
        print("Check: showCamera")
        self.yolo = Yolov8s("asset/best_nms_extended.onnx", "asset/dataset.yaml", confidence_thres=0.5, iou_thres=0.5) 
        print("Check: Yolov8s")
        self.cap = cv2.VideoCapture(video_config, cv2.CAP_GSTREAMER)
        print("Check: VideoCapture")
        pass

    def run(self):
        while self.cap.isOpened():
            success, img = self.cap.read()
            if success:  
                _, info = self.yolo.predict(img, returnImg= self.showCamera)
                if self.showCamera:
                    cv2.imshow("YOLOv8 Inference", _)
                
                try:
                    client_socket.sendall(bytes((str(info) + "\r\n"), "utf8"))
                    print('Server: {}\n'.format(info))
                except ConnectionResetError:
                    print("ConnectionResetError: Connection reset by peer")
                    break
            else:
                client_socket.sendall('Exit'.encode('utf-8'))	# Can't open camera!
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break   

        self.cap.release()
        cv2.destroyAllWindows()
        client_socket.close()
        server_socket.close()
        print("Check: Close")

if __name__ == '__main__':
    server = Server(parse_args())
    server.run()
