import os
import json
import joblib
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

def preprocess_frame(frame):
    target_size = (320, 420)  # Adjust the target size as needed
    resized_frame = cv2.resize(frame, target_size)
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    flattened_frame = gray_frame.flatten()
    return flattened_frame

def load_data(iteration_directory):
    metadata_path = os.path.join(iteration_directory, "metadata.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    images = []
    labels = []

    for entry in metadata:
        file_path = entry['file_path']
        label = entry['label']

        image = cv2.imread(file_path)
        preprocessed_image = preprocess_frame(image)

        images.append(preprocessed_image)
        labels.append(label)

    return images, labels

def train_model(images, labels):
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    X = np.array(images)
    y = np.array(encoded_labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")

    return model, label_encoder

if __name__ == '__main__':
    iteration_directory = 'labeled_data\iteration_20240516_130408'
    images, labels = load_data(iteration_directory)

    model, label_encoder = train_model(images, labels)

    model_path = os.path.join(iteration_directory, 'trained_model.pkl')
    label_encoder_path = os.path.join(iteration_directory, 'label_encoder.pkl')
    joblib.dump(model, model_path)
    joblib.dump(label_encoder, label_encoder_path)
    print(f"Trained model and label encoder saved to '{iteration_directory}'.")