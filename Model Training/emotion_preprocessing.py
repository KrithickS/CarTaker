import os
import numpy as np
import cv2
import tensorflow as tf
from tqdm import tqdm

# Define Image Size and Paths
IMG_SIZE = (48, 48)  # Resize images to 48x48
DATASET_PATH = "Datasets/emotion_detection"  # Change this to your dataset path
TRAIN_PATH = os.path.join(DATASET_PATH, "train")
TEST_PATH = os.path.join(DATASET_PATH, "test")

# Label Mapping
label_map = {emotion: idx for idx, emotion in enumerate(sorted(os.listdir(TRAIN_PATH)))}

# Function to load images and labels
def load_dataset(dataset_path):
    X, y = [], []
    
    for emotion in os.listdir(dataset_path):  # Iterate through emotion folders
        emotion_path = os.path.join(dataset_path, emotion)
        
        for file in tqdm(os.listdir(emotion_path), desc=f"Processing {emotion}"):
            img_path = os.path.join(emotion_path, file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Load in grayscale
            img = cv2.resize(img, IMG_SIZE)  # Resize
            
            X.append(img)
            y.append(label_map[emotion])
    
    X = np.array(X) / 255.0  # Normalize pixel values
    X = X.reshape(-1, IMG_SIZE[0], IMG_SIZE[1], 1)  # Add channel dimension
    y = np.array(y)

    # One-hot encoding of labels
    y = tf.keras.utils.to_categorical(y, num_classes=len(label_map))

    return X, y

# Load Train and Test Data
X_train, y_train = load_dataset(TRAIN_PATH)
X_test, y_test = load_dataset(TEST_PATH)

# Save Preprocessed Data
np.savez('preprocessed_image_data.npz', X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)

print("Preprocessing Complete. Data Saved.")
