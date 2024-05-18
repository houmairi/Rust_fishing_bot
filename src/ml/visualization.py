import os
import cv2
import joblib
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model, load_model

class CNNVisualization:
    def __init__(self, model):
        self.model = model

    def visualize_filters(self, layer_index):
        layer_output = self.model.layers[layer_index].output
        feature_extractor = Model(inputs=self.model.inputs, outputs=layer_output)

        # Generiere Testbilder für die Visualisierung (hier nur ein zufälliges Bild)
        input_shape = self.model.input_shape[1:]
        test_image = np.random.random((1, *input_shape))

        # Extrahiere die Merkmale aus dem ausgewählten Layer
        features = feature_extractor.predict(test_image)

        # Visualisiere die extrahierten Merkmale
        num_filters = features.shape[-1]
        fig, axes = plt.subplots(1, num_filters, figsize=(20, 2))
        for i in range(num_filters):
            axes[i].imshow(features[0, :, :, i], cmap='gray')
            axes[i].axis('off')
        plt.tight_layout()
        plt.show()

    def visualize_activation_maps(self, layer_index, image_path):
        layer_output = self.model.layers[layer_index].output
        feature_extractor = Model(inputs=self.model.inputs, outputs=layer_output)

        # Lade das Bild und führe die Vorverarbeitung durch
        image = cv2.imread(image_path)
        preprocessed_image = preprocess_frame(image)
        preprocessed_image = np.expand_dims(preprocessed_image, axis=0)
        preprocessed_image = np.expand_dims(preprocessed_image, axis=-1)

        # Extrahiere die Aktivierungskarten aus dem ausgewählten Layer
        activation_maps = feature_extractor.predict(preprocessed_image)

        # Visualisiere die Aktivierungskarten
        num_maps = activation_maps.shape[-1]
        fig, axes = plt.subplots(8, 8, figsize=(20, 20))
        for i in range(num_maps):
            row = i // 8
            col = i % 8
            axes[row, col].imshow(activation_maps[0, :, :, i], cmap='jet')
            axes[row, col].axis('off')
        plt.tight_layout()
        plt.show()

def preprocess_frame(frame):
    target_size = (320, 420)  # Anpassen der Zielgröße nach Bedarf
    resized_frame = cv2.resize(frame, target_size)
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    normalized_frame = gray_frame / 255.0  # Normalisierung der Pixelwerte
    return normalized_frame

if __name__ == '__main__':
    # Pfad zum Verzeichnis mit dem trainierten Modell und Label Encoder
    model_directory = 'labeled_data\\abgespeckt\\iteration_20240518_150914'

    # Lade das trainierte Modell und den Label Encoder
    model_path = os.path.join(model_directory, 'trained_model.keras')
    label_encoder_path = os.path.join(model_directory, 'label_encoder.pkl')
    model = load_model(model_path)
    label_encoder = joblib.load(label_encoder_path)

    # Festgelegter Bild-Pfad
    image_path = 'labeled_data\\iteration_20240516_190702\\high_2024-05-16 02-14-21_9.jpg'

    # Bild laden und vorverarbeiten
    image = cv2.imread(image_path)
    preprocessed_image = preprocess_frame(image)
    preprocessed_image = np.expand_dims(preprocessed_image, axis=0)
    preprocessed_image = np.expand_dims(preprocessed_image, axis=-1)

    # Vorhersage mit dem geladenen Modell
    prediction = model.predict(preprocessed_image)
    predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    print(f"Vorhergesagte Klasse: {predicted_label}")

    # Visualisierung der Aktivierungskarten
    visualizer = CNNVisualization(model)
    visualizer.visualize_activation_maps(layer_index=-4, image_path=image_path)