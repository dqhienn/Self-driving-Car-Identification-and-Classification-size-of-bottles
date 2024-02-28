import yaml
import cv2
import numpy as np
import onnxruntime as ort
import time

class Yolov8s:
    def __init__(self, onnx_model, yaml, confidence_thres, iou_thres):

        self.onnx_model = onnx_model
        self.confidence_thres = confidence_thres
        self.iou_thres = iou_thres
        self.yaml = yaml

        # Load the class names from the COCO dataset
        self.classes = self.loadClasses(self.yaml)

        # Generate a color palette for the classes
        self.color_palette = np.random.uniform(0, 255, size=(len(self.classes), 3))

                # Create an inference session using the ONNX model and specify execution providers
        self.session = ort.InferenceSession(self.onnx_model, providers=['CUDAExecutionProvider'])

        # Get the model inputs
        self.model_inputs = self.session.get_inputs()

        # Store the shape of the input for later use
        self.input_shape = self.model_inputs[0].shape
        self.input_width = self.input_shape[2]
        self.input_height = self.input_shape[3]

        self.dataResponse = ''

    def loadClasses(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            configfile = yaml.safe_load(file)
            return configfile['names']

    def draw_detections(self, img, box, score, class_id):
        """
        Draws bounding boxes and labels on the input image based on the detected objects.

        Args:
            img: The input image to draw detections on.
            box: Detected bounding box.
            score: Corresponding detection score.
            class_id: Class ID for the detected object.

        Returns:
            None
        """

        # Extract the coordinates of the bounding box
        x1, y1, w, h = box

        # Retrieve the color for the class ID
        color = self.color_palette[class_id]

        # Draw the bounding box on the image
        cv2.rectangle(img, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), color, 2)

        # Create the label text with class name and score
        label = f'{self.classes[class_id]}: {score:.2f}'

        # Calculate the dimensions of the label text
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

        # Calculate the position of the label text
        label_x = x1
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 10

        # Draw a filled rectangle as the background for the label text
        cv2.rectangle(img, (label_x, label_y - label_height), (label_x + label_width, label_y + label_height), color,
                      cv2.FILLED)

        # Draw the label text on the image
        cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    def preprocess(self, img):
        """
        Preprocesses the input image before performing inference.

        Returns:
            image_data: Preprocessed image data ready for inference.
        """

        # Get the height and width of the input image
        self.img_height, self.img_width = img.shape[:2]

        # Convert the image color space from BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize the image to match the input shape
        img = cv2.resize(img, (self.input_width, self.input_height))

        # Normalize the image data by dividing it by 255.0
        image_data = np.array(img) / 255.0

        # Transpose the image to have the channel dimension as the first dimension
        image_data = np.transpose(image_data, (2, 0, 1))  # Channel first

        # Expand the dimensions of the image data to match the expected input shape
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)

        # Return the preprocessed image data
        return image_data

    def postprocess(self, input_image, output):
        """
        Performs post-processing on the model's output to extract bounding boxes, scores, and class IDs.

        Args:
            input_image (numpy.ndarray): The input image.
            output (numpy.ndarray): The output of the model.

        Returns:
            numpy.ndarray: The input image with detections drawn on it.
        """
        info = [[],[]]

        # Lists to store the bounding boxes, scores, and class IDs of the detections
        boxes = output[0][0]
        scores = output[1][0]
        class_ids = output[2][0]

        # Calculate the scaling factors for the bounding box coordinates
        x_factor = self.img_width / self.input_width
        y_factor = self.img_height / self.input_height

        # Calculate the scaled coordinates of the bounding box
        for i in range(len(boxes)):
            x, y, w, h = boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]
            left = int((x - w / 2) * x_factor)
            top = int((y - h / 2) * y_factor)
            width = int(w * x_factor)
            height = int(h * y_factor)
            self.draw_detections(input_image, [left, top, width, height], scores[i], class_ids[i])

            info[0].append(class_ids[i])
            info[1].append(top + height)

        return  input_image, info

    def predict(self, img, returnImg):
        """
        Performs inference using an ONNX model and returns the output image with drawn detections.

        Returns:
            output_img: The output image with drawn detections.
        """
        # Preprocess the image data
        # a = time.time()
        img_data = self.preprocess(img)
        # print(f"Time preprocess:{time.time() - a}")
        
        # Run inference using the preprocessed image data
        # a = time.time()
        outputs = self.session.run(None, {self.model_inputs[0].name: img_data})
        # print(f"Time infent:{time.time() - a}")

        # Perform post-processing on the outputs to obtain output image.
        # a = time.time()
        # class_ids = outputs[2][0]
        # boxes = outputs[0][0]
        
        img, info = self.postprocess(img, outputs)  # output image
        if returnImg:
            return img, info
        else:
            return (None, info)