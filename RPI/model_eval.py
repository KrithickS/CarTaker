import cv2
import numpy as np
import os
import time
from tensorflow.keras.models import load_model
import tensorflow as tf

# Constants
IMG_SIZE = (48, 48)
MODEL_PATH = '/home/thala/model1.h5'
IMAGE_PATH = '/home/thala/high_quality_image.jpg'  # Hardcoded path to the image
LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Load model and face detector
model = load_model(MODEL_PATH)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Preprocess the face
def preprocess_face(face):
    face = cv2.resize(face, IMG_SIZE)
    face = face / 255.0
    face = face.reshape(1, IMG_SIZE[0], IMG_SIZE[1], 1)
    return face

# Run prediction
def predict_emotion(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"[{time.ctime()}] Error: Couldn't load image: {image_path}")
        with open("face.status","w") as f:
        	f.write("0\n")
        return "Image not found"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        print(f"[{time.ctime()}] No face detected.")
        with open("face.status","w") as f:
        	f.write("0\n")
        return "No face detected"

    print(f"[{time.ctime()}] Face detected.")
    with open("face.status","w") as f:
        	f.write("1\n")
    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face_input = preprocess_face(face)
        predictions = model.predict(face_input, verbose=0)
        predicted_index = np.argmax(predictions)
        emotion = LABELS[predicted_index]
        confidence = predictions[0][predicted_index]

        print(f"Detected Emotion: {emotion} ({confidence:.2f} confidence)")

        # Draw box and label on original image (optional display)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(image, f"{emotion} ({confidence:.2f})", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

        # Optional: display result
        # cv2.imshow("Prediction", image)
        # cv2.waitKey(1)

    return "Face detected"

# Monitor image for changes
def watch_image(image_path, check_interval=2):
    print("Watching for changes in:", image_path)
    last_modified = None

    while True:
        try:
            if os.path.exists(image_path):
                current_modified = os.path.getmtime(image_path)
                if last_modified is None or current_modified != last_modified:
                    print("\n--- Change Detected ---")
                    last_modified = current_modified
                    predict_emotion(image_path)
            else:
                print(f"[{time.ctime()}] File not found: {image_path}")
        except Exception as e:
            print(f"[{time.ctime()}] Error: {e}")

        time.sleep(check_interval)  # Check every N seconds

# Start watching
watch_image(IMAGE_PATH, check_interval=2)
