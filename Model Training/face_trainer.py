import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, Callback, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
import tensorflow as tf
import os
import logging
from pathlib import Path

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=str(log_dir / "face_detection_training.log"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Custom callback for logging each epoch
class LoggingCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logging.info(f"Epoch {epoch+1} - loss: {logs.get('loss', 'N/A'):.4f} - accuracy: {logs.get('accuracy', 'N/A'):.4f} - val_loss: {logs.get('val_loss', 'N/A'):.4f} - val_accuracy: {logs.get('val_accuracy', 'N/A'):.4f}")

# Load preprocessed data
data = np.load('face_detection_preprocessed.npz')
X_train, X_valid, y_train, y_valid = data['X_train'], data['X_valid'], data['y_train'], data['y_valid']
print(f"Training Data: {X_train.shape}, Labels: {y_train.shape}")
print(f"Validation Data: {X_valid.shape}, Labels: {y_valid.shape}")
logging.info(f"Training Data: {X_train.shape}, Labels: {y_train.shape}")
logging.info(f"Validation Data: {X_valid.shape}, Labels: {y_valid.shape}")

# Model parameters
img_width, img_height, img_depth = X_train.shape[1], X_train.shape[2], X_train.shape[3]
num_classes = y_train.shape[1]  # For face detection, this is typically 1 (face or no face)

# Define Model with L2 regularization added to convolutional and dense layers
def build_face_detection_net():
    model = Sequential(name='FaceDetectionCNN')
    reg = l2(1e-4)  # L2 regularization factor
    
    # First block
    model.add(Conv2D(32, (3,3), activation='relu', padding='same',
                     input_shape=(img_width, img_height, img_depth),
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(Conv2D(32, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.35))
    
    # Second block
    model.add(Conv2D(64, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.35))
    
    # Third block
    model.add(Conv2D(128, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(Conv2D(128, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.45))
    
    # Fourth block
    model.add(Conv2D(256, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(Conv2D(256, (3,3), activation='relu', padding='same',
                     kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.45))
    
    # Flatten and dense layers
    model.add(Flatten())
    model.add(Dense(256, activation='relu', kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(Dropout(0.55))
    model.add(Dense(128, activation='relu', kernel_initializer='he_normal', kernel_regularizer=reg))
    model.add(BatchNormalization())
    model.add(Dropout(0.55))
    
    # Output layer
    model.add(Dense(num_classes, activation='sigmoid'))
    
    model.compile(
        loss='binary_crossentropy',  # Change to 'mse' if doing bounding box regression
        optimizer=Adam(learning_rate=0.0005),  # Lower learning rate for finer tuning
        metrics=['accuracy']
    )
    return model

# Log model architecture
logging.info("Building face detection model with enhanced augmentation, early stopping, and L2 regularization...")
model = build_face_detection_net()
model_summary = []
model.summary(print_fn=lambda x: model_summary.append(x))
logging.info("Model architecture:\n" + "\n".join(model_summary))

# Callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1)
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=1e-7, verbose=1)
# Updated file extension to .keras as required
model_checkpoint = ModelCheckpoint("best_face_detection_model.keras", monitor='val_loss', save_best_only=True, verbose=1)
logging_callback = LoggingCallback()

# Enhanced Data Augmentation with more aggressive transformations
train_datagen = ImageDataGenerator(
    rotation_range=40,             # increased rotation range
    width_shift_range=0.4,         # increased width shift
    height_shift_range=0.4,        # increased height shift
    shear_range=0.4,               # increased shear range
    zoom_range=0.4,                # increased zoom
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],     # enhanced brightness variation
    fill_mode='nearest'
)
train_datagen.fit(X_train)

logging.info("Starting training with enhanced data augmentation, early stopping, and improved regularization...")
history = model.fit(
    train_datagen.flow(X_train, y_train, batch_size=16),
    validation_data=(X_valid, y_valid),
    epochs=50,
    callbacks=[early_stopping, lr_scheduler, model_checkpoint, logging_callback]
)

logging.info(f"Training completed after {len(history.epoch)} epochs")
logging.info(f"Best validation loss: {min(history.history['val_loss']):.4f}")

# Save Final Model
model.save("final_face_detection_model.keras")
print("Final model saved as final_face_detection_model.keras")
logging.info("Final model saved as final_face_detection_model.keras")

# Plot Training History
sns.set()
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
# Accuracy Plot
sns.lineplot(x=history.epoch, y=history.history['accuracy'], label='Train', ax=axes[0])
sns.lineplot(x=history.epoch, y=history.history['val_accuracy'], label='Validation', ax=axes[0])
axes[0].set_title('Accuracy')
# Loss Plot
sns.lineplot(x=history.epoch, y=history.history['loss'], label='Train', ax=axes[1])
sns.lineplot(x=history.epoch, y=history.history['val_loss'], label='Validation', ax=axes[1])
axes[1].set_title('Loss')
plt.tight_layout()
plt.savefig('face_detection_history.png')
logging.info("Training history plot saved as face_detection_history.png")
plt.show()
