import tensorflow as tf
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.models import Sequential
import os
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
MODEL_SAVE_PATH = 'model/satellite_model.h5'

print("--- Training Upgraded Satellite Image Analysis Model ---")

# 1. Load and Preprocess the CIFAR-10 Data
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

# Normalize pixel values to be between 0 and 1
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# Define class names for context
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

print(f"Loaded {len(x_train)} real-world color images for training.")
print(f"Image shape: {x_train.shape[1:]}") # Should be (32, 32, 3)

# 2. Build the Upgraded CNN Model
# This model is deeper to handle the complexity of color images.
model = Sequential([
    Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(32, 32, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    
    Conv2D(64, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5), # Dropout layer to prevent overfitting
    Dense(10, activation='softmax') # 10 outputs, one for each class
])

# 3. Compile and Train
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

print("Training the upgraded CNN model... (This may take a few minutes)")
model.fit(x_train, y_train, epochs=15, batch_size=64, validation_split=0.1, verbose=2)

# 4. Evaluate and Save
print("\nEvaluating model performance...")
loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
print(f"**Model Accuracy on Test Images: {accuracy*100:.2f}%**")

os.makedirs('model', exist_ok=True)
model.save(MODEL_SAVE_PATH)
print(f"Upgraded satellite model saved successfully to '{MODEL_SAVE_PATH}'!")
