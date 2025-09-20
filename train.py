import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import re

# Suppress TensorFlow informational messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# --- Configuration ---
DATA_FILE_PATH = 'data/training_data.csv'
MODEL_SAVE_PATH = 'model/strategic_model.h5'

# 1. Load Data
print(f"Loading data from '{DATA_FILE_PATH}'...")
missing_value_formats = ["n.a.","?","NA","n/a", "na", "--", "null", "NaN", ""]
data = pd.read_csv(DATA_FILE_PATH, thousands=',', na_values=missing_value_formats)
print("Data loaded successfully.")

# 2. Automated Data Cleaning & Preprocessing Pipeline
print("\n--- Starting Data Cleaning Pipeline ---")

#   a. Drop irrelevant columns
if 'engagement_id' in data.columns and 'detection_timestamp' in data.columns:
    data.drop(columns=['engagement_id', 'detection_timestamp'], inplace=True)
    print("[CLEAN] Dropped irrelevant columns.")

#   b. Standardize categorical columns
categorical_cols = [col for col in ['radar_type', 'is_jamming', 'weather_conditions'] if col in data.columns]
for col in categorical_cols:
    data[col] = data[col].str.lower()
data.replace({'active array': 'aesa', 'y': 'yes', 'n': 'no', 'clear skies': 'clear'}, inplace=True)
if categorical_cols:
    data = pd.get_dummies(data, columns=categorical_cols, dummy_na=True)
    print("[CLEAN] Converted categorical columns to numerical format.")

#   c. Clean and convert altitude column to numeric BEFORE other steps
if 'own_jet_altitude_m' in data.columns:
    data['own_jet_altitude_m'] = pd.to_numeric(data['own_jet_altitude_m'].astype(str).str.replace(r'[^0-9\.-]', '', regex=True), errors='coerce')
    print("[CLEAN] Converted 'own_jet_altitude_m' column to a pure number.")

#   d. Handle Missing Values in all numerical columns
for col in data.select_dtypes(include=np.number).columns:
    if data[col].isnull().any():
        median_val = data[col].median()
        data[col].fillna(median_val, inplace=True)
        print(f"[CLEAN] Missing numerical values in '{col}' filled with median ({median_val:.2f}).")

#   e. Correct Outliers and Impossible Values
data['signal_strength_db'] = data['signal_strength_db'].apply(lambda x: -abs(float(x)))
data['threat_priority_level'] = data['threat_priority_level'].clip(lower=1, upper=3).astype(int)
data['own_jet_altitude_m'] = data['own_jet_altitude_m'].clip(lower=1000, upper=25000)
data['frequency_ghz'] = data['frequency_ghz'].clip(lower=1, upper=20)
print("[CLEAN] Corrected outliers in numerical columns.")

print("--- Data Cleaning Complete ---")


# 3. Feature Engineering
print("\nPreparing data for AI model...")
X = data.drop('action_ping_back', axis=1)
y = data['action_ping_back']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("Data prepared successfully.")


# 4. Build and Train the AI Model
print("\n--- Starting Model Training ---")
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train_scaled, y_train, epochs=200, batch_size=8, verbose=0)
print("Model training complete.")


# 5. Evaluate and Save
print("\n--- Evaluating Model Performance ---")
loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"**Model Accuracy on Cleaned Test Data: {accuracy*100:.2f}%**")

os.makedirs('model', exist_ok=True)
model.save(MODEL_SAVE_PATH)
print(f"Model saved successfully to '{MODEL_SAVE_PATH}'!")
