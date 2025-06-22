import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, Callback
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import os
import logging
from pathlib import Path

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=str(log_dir / "training.log"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Custom callback for logging each epoch
class LoggingCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logging.info(f"Epoch {epoch+1} - loss: {logs.get('loss', 'N/A'):.4f} - accuracy: {logs.get('accuracy', 'N/A'):.4f} - val_loss: {logs.get('val_loss', 'N/A'):.4f} - val_accuracy: {logs.get('val_accuracy', 'N/A'):.4f}")

# Load preprocessed data
data = np.load('preprocessed_data.npz')
X_train, X_valid, y_train, y_valid = data['X_train'], data['X_valid'], data['y_train'], data['y_valid']
# Print dataset shapes
print(f"Training Data: {X_train.shape}, Labels: {y_train.shape}")
print(f"Validation Data: {X_valid.shape}, Labels: {y_valid.shape}")
logging.info(f"Training Data: {X_train.shape}, Labels: {y_train.shape}")
logging.info(f"Validation Data: {X_valid.shape}, Labels: {y_valid.shape}")

# Model parameters
img_width, img_height, img_depth = X_train.shape[1], X_train.shape[2], X_train.shape[3]
num_classes = y_train.shape[1]
# Define Model
def build_net():
    model = Sequential(name='DCNN')
    model.add(Conv2D(64, (5,5), activation='elu', padding='same', input_shape=(img_width, img_height, img_depth), kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (5,5), activation='elu', padding='same', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.4))
    model.add(Conv2D(128, (3,3), activation='elu', padding='same', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(Conv2D(128, (3,3), activation='elu', padding='same', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.4))
    model.add(Conv2D(256, (3,3), activation='elu', padding='same', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(Conv2D(256, (3,3), activation='elu', padding='same', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(128, activation='elu', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(Dropout(0.6))
    model.add(Dense(num_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
    return model

# Log model architecture
logging.info("Building model...")
model = build_net()
model_summary = []
model.summary(print_fn=lambda x: model_summary.append(x))
logging.info("Model architecture:\n" + "\n".join(model_summary))

# Callbacks
early_stopping = EarlyStopping(monitor='val_accuracy', patience=11, restore_best_weights=True, verbose=1)
lr_scheduler = ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=7, min_lr=1e-7, verbose=1)
logging_callback = LoggingCallback()

# Data Augmentation
train_datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True
)
train_datagen.fit(X_train)

# Log training start
logging.info("Starting model training with the following parameters:")
logging.info(f"Batch size: 32, Learning rate: 0.001, Epochs: 50")
logging.info(f"Data augmentation: rotation=15°, width_shift=0.15, height_shift=0.15, shear=0.15, zoom=0.15, horizontal_flip=True")

# Train Model
history = model.fit(
    train_datagen.flow(X_train, y_train, batch_size=32),
    validation_data=(X_valid, y_valid),
    epochs=50,
    callbacks=[early_stopping, lr_scheduler, logging_callback]
)

# Log training completion
logging.info(f"Training completed after {len(history.epoch)} epochs")
logging.info(f"Best validation accuracy: {max(history.history['val_accuracy']):.4f}")

# Save Model
model.save("model1.h5")
print("Model saved as model.h5")
logging.info("Model saved as model1.h5")

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
plt.savefig('epoch_history_dcnn.png')
logging.info("Training history plot saved as epoch_history_dcnn.png")
plt.show()
