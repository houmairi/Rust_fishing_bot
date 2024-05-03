import os
import json
import joblib
import numpy as np
import cv2
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def load_data(data_directory):
    metadata_path = os.path.join(data_directory, "metadata.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    images = []
    labels = []

    for entry in metadata:
        file_path = entry['file_path']
        label = entry['label']

        # Load the image
        image = cv2.imread(file_path)

        images.append(image)
        labels.append(label)

    return images, labels

def preprocess_image(image):
    # Preprocess the image (resize, normalize, etc.)
    # Modify this function to match the exact dimensions and color channels used during training
    preprocessed_image = cv2.resize(image, (2560, 1440))  # Adjust the size to match the training preprocessing
    preprocessed_image = preprocessed_image.flatten()  # Flatten the image
    return preprocessed_image

def predict_label(model, image):
    # Preprocess the image
    preprocessed_image = preprocess_image(image)

    # Make predictions using the loaded model
    predicted_label = model.predict([preprocessed_image])

    return predicted_label[0]

if __name__ == '__main__':
    model_directory = 'data2process/iteration_20240503_171233'  # Replace with the actual directory path of the trained model
    test_data_directory = 'data2process/iteration_20240503_171501'  # Replace with the actual directory path of the preprocessed test data

    # Load the trained model and label encoder
    model_path = os.path.join(model_directory, 'trained_model.pkl')
    label_encoder_path = os.path.join(model_directory, 'label_encoder.pkl')
    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)

    # Load the preprocessed test data
    test_images, test_labels = load_data(test_data_directory)

    # Visualize the key inputs and predictions
    for image, true_label in zip(test_images, test_labels):
        predicted_label_encoded = predict_label(model, image)
        predicted_label = label_encoder.inverse_transform([predicted_label_encoded])[0]

        # Display the image
        cv2.imshow('Frame', image)
        cv2.waitKey(100)  # Adjust the delay as needed

        # Print the true and predicted labels
        print(f"True Label: {true_label}, Predicted Label: {predicted_label}")

    cv2.destroyAllWindows()

    # Make predictions for evaluation
    predictions = []
    for image in test_images:
        predicted_label_encoded = predict_label(model, image)
        predictions.append(predicted_label_encoded)

    # Decode the predicted labels
    decoded_predictions = label_encoder.inverse_transform(predictions)

    # Evaluate the model's performance
    accuracy = accuracy_score(test_labels, decoded_predictions)
    precision = precision_score(test_labels, decoded_predictions, average='weighted')
    recall = recall_score(test_labels, decoded_predictions, average='weighted')
    f1 = f1_score(test_labels, decoded_predictions, average='weighted')
    cm = confusion_matrix(test_labels, decoded_predictions)

    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-score: {f1:.2f}")
    print("Confusion Matrix:")
    print(cm)