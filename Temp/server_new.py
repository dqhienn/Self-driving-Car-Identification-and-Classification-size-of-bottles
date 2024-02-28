import cv2
import logging
import socket
import argparse
from yolo.YoloV8 import Yolov8s

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

# Constants
SERVER_ADDRESS = ('127.0.0.1', 12345)

class Server:
    def __init__(self, args):
        self.show_camera = args.sc
        logging.info("Initializing YOLOv8 model...")
        self.yolo = Yolov8s("asset/best_nms_extended.onnx", "asset/dataset.yaml", confidence_thres=0.5, iou_thres=0.5)
        logging.info("Initializing video capture...")
        self.cap = cv2.VideoCapture('v4l2src device=/dev/video0 ! video/x-raw, format=YUY2, width=640, height=480, framerate=30/1 ! nvvidconv ! video/x-raw(memory:NVMM) ! nvvidconv ! video/x-raw, format=BGRx !  videoconvert ! video/x-raw, format=BGR ! appsink', cv2.CAP_GSTREAMER)
        logging.info("Initialization complete.")

    def run(self):
        logging.info("Server is listening for connections...")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(1)
        logging.info("Waiting for a connection...")

        client_socket, client_address = server_socket.accept()
        logging.info("Connected: %s", client_address)

        while self.cap.isOpened():
            success, img = self.cap.read()
            if success:
                _, info = self.yolo.predict(img, returnImg=self.show_camera)
                if self.show_camera:
                    cv2.imshow("YOLOv8 Inference", _)

                '''
                if len(info[0]) > 0:
                    client_socket.sendall(bytes((str(info) + "\r\n"), "utf-8"))
                    logging.info('Server: %s', info)
                '''

                if len(info[0]) > 0:
                    # Find new detections
                    new_detections = set(zip(info[0], info[1])) - self.prev_detections
                    if new_detections:
                        # Send the new detections
                        message = ', '.join([f"id: {i}, bottomLine: {b}" for i, b in new_detections])
                        client_socket.sendall(bytes((message + "\r\n"), "utf-8"))
                        logging.info('Server: %s', new_detections)
                        # Update previous detections
                        self.prev_detections.update(new_detections)

            else:
                client_socket.sendall('Exit'.encode('utf-8'))  # Can't open camera! Sen mess "Exit" to Client
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        logging.info("Video capture released.")
        cv2.destroyAllWindows()
        logging.info("OpenCV windows destroyed.")
        server_socket.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sc', action='store_true', default=False, help='Set value to encode view camera')
    args = parser.parse_args()
    logging.info("Arguments: %s", args)
    return args

if __name__ == '__main__':
    args = parse_args()
    server = Server(args)
    server.run()
