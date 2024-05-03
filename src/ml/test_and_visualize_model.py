import os
import json
import cv2
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def load_data(data_directory):
    with open(os.path.join(data_directory, "annotations.json"), 'r') as f:
        annotations = json.load(f)

    frames = []
    labels = []

    for annotation in annotations:
        frame_path = os.path.join(data_directory, annotation['frame'])
        frame = cv2.imread(frame_path)
        frames.append(frame)
        labels.append(annotation['label'])

    return frames, labels

# Load the trained model and label encoder
model = joblib.load('trained_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Load the preprocessed data
data_directory = 'C:/Users/Niko/Documents/Repositorys/rust-fishing-bot/src/ml/data2process'
frames, labels = load_data(data_directory)

# Make predictions
predictions = model.predict(frames)

# Decode the predicted labels
decoded_predictions = label_encoder.inverse_transform(predictions)

# Visualize the key inputs and predictions
for frame, true_label, pred_label in zip(frames, labels, decoded_predictions):
    cv2.imshow('Frame', frame)
    cv2.waitKey(100)  # Adjust the delay as needed
    print(f"True Label: {true_label}, Predicted Label: {pred_label}")

cv2.destroyAllWindows()

# Evaluate the model's performance
accuracy = accuracy_score(labels, decoded_predictions)
precision = precision_score(labels, decoded_predictions, average='weighted')
recall = recall_score(labels, decoded_predictions, average='weighted')
f1 = f1_score(labels, decoded_predictions, average='weighted')
cm = confusion_matrix(labels, decoded_predictions)

print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1-score: {f1:.2f}")
print("Confusion Matrix:")
print(cm)