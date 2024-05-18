import os
import json
import joblib
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

def preprocess_frame(frame):
    target_size = (320, 420)  # Adjust the target size as needed
    resized_frame = cv2.resize(frame, target_size)
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    normalized_frame = gray_frame / 255.0  # Normalize pixel values
    return normalized_frame

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

def create_cnn_model(input_shape, num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    return model

def train_model(images, labels):
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    one_hot_labels = to_categorical(encoded_labels)

    X = np.array(images)
    y = np.array(one_hot_labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    input_shape = (X.shape[1], X.shape[2], 1)
    num_classes = len(label_encoder.classes_)

    model = create_cnn_model(input_shape, num_classes)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

    y_pred = model.predict(X_test)
    y_pred_labels = np.argmax(y_pred, axis=1)
    y_test_labels = np.argmax(y_test, axis=1)
    accuracy = accuracy_score(y_test_labels, y_pred_labels)
    print(f"Model accuracy: {accuracy:.2f}")

    return model, label_encoder

if __name__ == '__main__':
    iteration_directory = 'labeled_data/abgespeckt/iteration_20240518_150914'
    images, labels = load_data(iteration_directory)

    model, label_encoder = train_model(images, labels)

    model_path = os.path.join(iteration_directory, 'trained_model.keras')
    label_encoder_path = os.path.join(iteration_directory, 'label_encoder.pkl')
    model.save(model_path)
    joblib.dump(label_encoder, label_encoder_path)
    print(f"Trained model and label encoder saved to '{iteration_directory}'.")