import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Flatten
from tensorflow.keras.callbacks import LearningRateScheduler

# Ensure correct path setup for your environment
dataset_path = "C:/Users/sraad/Downloads/archive/real_and_fake_face"
val_path = dataset_path  # Assuming validation data is within the same dataset path

# Data augmentation setup
data_with_aug = ImageDataGenerator(horizontal_flip=True,
                                   vertical_flip=False,
                                   rescale=1./255,
                                   validation_split=0.2)

train = data_with_aug.flow_from_directory(dataset_path,
                                          class_mode="binary",
                                          target_size=(224, 224),  # Updated to match VGG16 input
                                          batch_size=32,
                                          subset="training")

val = data_with_aug.flow_from_directory(dataset_path,
                                        class_mode="binary",
                                        target_size=(224, 224),  # Updated to match VGG16 input
                                        batch_size=32,
                                        subset="validation")

# Load the MobileNetV2 model
mnet = MobileNetV2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))

# Model setup
model = Sequential([
    mnet,
    GlobalAveragePooling2D(),
    Dense(512, activation="relu"),
    Dense(2, activation="softmax")
])

model.layers[0].trainable = False
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

# Callbacks setup
def scheduler(epoch, lr):
    if epoch < 5:
        return lr
    else:
        return lr * tf.math.exp(-0.1)

callback_list = [LearningRateScheduler(scheduler)]

# Model training
hist = model.fit(train, epochs=20, validation_data=val, callbacks=callback_list)

# Visualization of training
epochs = range(20)
plt.figure(figsize=(14, 5))

# Loss
plt.subplot(1, 2, 1)
plt.plot(epochs, hist.history['loss'], label='Training Loss')
plt.plot(epochs, hist.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# Accuracy
plt.subplot(1, 2, 2)
plt.plot(epochs, hist.history['accuracy'], label='Training Accuracy')
plt.plot(epochs, hist.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.show()

# Function to load and preprocess images
def load_img(path):
    image = cv2.imread(path)
    if image is None:
        print(f"Warning: Unable to load image at {path}")
        return np.zeros((224, 224, 3))  # Return a blank array if image cannot be loaded
    image = cv2.resize(image, (224, 224))
    return image[..., ::-1]

# Predictions and visualization
predictions = model.predict(val, steps=val.n // val.batch_size+1)  # Updated to use predict

# Display some predictions
plt.figure(figsize=(15, 15))
start_index = 0  # Updated for demonstration purposes, adjust as necessary

for i in range(16):
    plt.subplot(4, 4, i + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)

    pred = np.argmax(predictions[i + start_index])
    actual = val.labels[i + start_index]
    label = "Fake" if pred == 0 else "Real"
    color = "green" if pred == actual else "red"

    plt.xlabel(f"Pred: {label}", color=color)
    img_path = os.path.join(dataset_path, val.filepaths[i + start_index])
    plt.imshow(load_img(img_path))

plt.tight_layout()
plt.show()
