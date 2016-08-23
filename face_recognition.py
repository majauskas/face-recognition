from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2, os
import sys
import json
import imutils
import signal
import numpy as np
from PIL import Image


def to_node(type, message):
    try:
        print(json.dumps({type: message}))
    except Exception:
        pass
    # stdout has to be flushed manually to prevent delays in the node helper communication
    sys.stdout.flush()


def shutdown(self, signum):
    to_node("status", 'Shutdown -- Cleaning up camera...')
    camera.stop()
    camera.join()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)

FACE_WIDTH = 92
FACE_HEIGHT = 112
HAAR_SCALE_FACTOR = 1.3
HAAR_MIN_NEIGHBORS = 4
HAAR_MIN_SIZE = (30, 30)



def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.sad')]
    images = []
    labels = []
    for image_path in image_paths:        
        image_pil = Image.open(image_path)
        image = np.array(image_pil, 'uint8')
        nbr = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        images.append(image)
        labels.append(nbr) 
    return images, labels


def detect_single(image):
    faces = haar_faces.detectMultiScale(image, scaleFactor=HAAR_SCALE_FACTOR, minNeighbors=HAAR_MIN_NEIGHBORS, minSize=HAAR_MIN_SIZE, flags=cv2.CASCADE_SCALE_IMAGE)
    if len(faces) != 1:
        return None
    return faces[0]


def crop(image, x, y, w, h):
    crop_height = int((FACE_HEIGHT / float(FACE_WIDTH)) * w)
    midy = y + h / 2
    y1 = max(0, midy - crop_height / 2)
    y2 = min(image.shape[0] - 1, midy + crop_height / 2)
    return image[y1:y2, x:x + w]


def resize(image):
    return cv2.resize(image, (FACE_WIDTH, FACE_HEIGHT), interpolation=cv2.INTER_LANCZOS4)



haar_faces = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
recognizer = cv2.createLBPHFaceRecognizer(threshold=100)

images, labels = get_images_and_labels("./faces")
recognizer.train(images, np.array(labels))


camera = PiCamera()
camera.rotation = 180
camera.framerate = 25
camera.led = False
camera.resolution = (640, 360)
rawCapture = PiRGBArray(camera, size=(640, 360))
#camera.resolution = (160, 120)
#rawCapture = PiRGBArray(camera, size=(160, 120))

   
i = 137
time.sleep(0.1)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)    
    result = detect_single(image)
    if result is not None: 
        x, y, w, h = result                 
        resizedImage = crop(image, x, y, w, h)     
        label, conf = recognizer.predict(resizedImage)
        
        if (label != -1 and label != 0):
             #print label, conf
             to_node("face", label)
        if (label == -1):
          #i = i+1
          print "new face"
          #cv2.imwrite("./faces/subject29." + str(i) + ".jpg", resizedImage)
          #images, labels = get_images_and_labels("./faces")
          #recognizer.train(images, np.array(labels))
          

    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
        
  
        

