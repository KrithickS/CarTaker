import os
import numpy as np
import cv2
import tensorflow as tf
from tqdm import tqdm
from sklearn.model_selection import train_test_split

# Define Image Size and Paths
IMG_SIZE = (224, 224)  # Resize images to 224x224 for face detection (larger than emotion)
DATASET_PATH = "Datasets/face_detection"  # Change this to your dataset path
IMAGES_PATH = os.path.join(DATASET_PATH, "images")
LABELS_PATH = os.path.join(DATASET_PATH, "labels")
TRAIN_IMAGES_PATH = os.path.join(IMAGES_PATH, "train")
VAL_IMAGES_PATH = os.path.join(IMAGES_PATH, "val")

# Function to parse YOLO format label file
def parse_yolo_label(label_path, image_width, image_height):
    """
    Parse YOLO format label file and return bounding box coordinates
    Format: class_id x_center y_center width height
    Values are normalized (0-1)
    """
    bboxes = []
    
    try:
        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                values = line.strip().split()
                if len(values) == 5:  # class_id, x, y, w, h
                    class_id = int(values[0])
                    x_center = float(values[1])
                    y_center = float(values[2])
                    width = float(values[3])
                    height = float(values[4])
                    
                    # Keep values normalized
                    bboxes.append([class_id, x_center, y_center, width, height])
    except Exception as e:
        print(f"Error parsing label file {label_path}: {e}")
    
    return bboxes

# Function to load images and labels
def load_face_dataset(images_dir, labels_dir):
    """
    Load face detection dataset with images and bounding box labels
    """
    X, y = [], []
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    for image_file in tqdm(image_files, desc=f"Processing {os.path.basename(images_dir)}"):
        img_path = os.path.join(images_dir, image_file)
        
        # Get corresponding label file (same name but .txt extension)
        label_file = os.path.splitext(image_file)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)
        
        # Read image
        img = cv2.imread(img_path)
        
        if img is not None:
            # Get original dimensions for label parsing
            orig_height, orig_width = img.shape[:2]
            
            # Resize image
            img = cv2.resize(img, IMG_SIZE)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
            
            # Parse label
            bboxes = parse_yolo_label(label_path, orig_width, orig_height)
            
            # Store image and labels
            X.append(img)
            y.append(bboxes)
    
    # Convert to numpy arrays
    X = np.array(X, dtype='float32') / 255.0  # Normalize pixel values
    
    # For y, we need to handle variable number of bounding boxes per image
    # For simplicity, we'll take the first bounding box for each image
    # In a more advanced implementation, you would handle multiple bounding boxes
    y_processed = []
    for boxes in y:
        if boxes:  # If there are any bounding boxes
            y_processed.append(boxes[0])  # Take the first box
        else:
            # No faces in this image - use a dummy box with confidence 0
            y_processed.append([0, 0, 0, 0, 0])
    
    y = np.array(y_processed, dtype='float32')
    
    return X, y

# Load Train and Val Data
print("Loading training data...")
X_train, y_train = load_face_dataset(TRAIN_IMAGES_PATH, os.path.join(LABELS_PATH, "train"))
print("Loading validation data...")
X_val, y_val = load_face_dataset(VAL_IMAGES_PATH, os.path.join(LABELS_PATH, "val"))

# Print dataset information
print(f"Training images: {len(X_train)}, shape: {X_train.shape}")
print(f"Validation images: {len(X_val)}, shape: {X_val.shape}")
print(f"Training labels shape: {y_train.shape}")
print(f"Validation labels shape: {y_val.shape}")

# Save Preprocessed Data
np.savez('face_detection_preprocessed.npz', 
         X_train=X_train, 
         X_valid=X_val, 
         y_train=y_train, 
         y_valid=y_val)

print("Preprocessing Complete. Data Saved to face_detection_preprocessed.npz")
