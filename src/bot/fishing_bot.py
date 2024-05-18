import sys
import os
import time
from pytesseract import TesseractNotFoundError
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from src.sound.sound_detection import FishBiteDetector
from src.bot.fish_caught_detector import FishCaughtDetector
from src.bot.game_interaction import GameInteraction
import keyboard
import joblib
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from mss import mss

class FishingBot:
    def __init__(self, game_interaction):
        self.game_interaction = game_interaction
        self.fish_bite_detector = FishBiteDetector()
        self.is_running = False
        self.fish_caught_detector = FishCaughtDetector()
        self.model = None
        self.label_encoder = None

    def load_model(self, model_path, label_encoder_path):
        self.model = load_model(model_path)
        self.label_encoder = joblib.load(label_encoder_path)

    def preprocess_frame(self, frame):
        target_size = (320, 420)  # Adjust the target size as needed
        resized_frame = cv2.resize(frame, target_size)
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        normalized_frame = gray_frame / 255.0  # Normalize pixel values
        expanded_frame = np.expand_dims(normalized_frame, axis=0)
        expanded_frame = np.expand_dims(expanded_frame, axis=-1)
        return expanded_frame

    def predict_tension(self, frame):
        preprocessed_frame = self.preprocess_frame(frame)
        predicted_label_encoded = self.model.predict(preprocessed_frame)
        predicted_label = self.label_encoder.inverse_transform(predicted_label_encoded.argmax(axis=1))[0]
        return predicted_label

    def start_fishing(self):
        self.is_running = True
        print("Fishing bot started. Press 'Esc' to stop.")
        self.fish_bite_detector.start_detection()
        self.game_recognition_loop()

        self.stop_fishing()

    def stop_fishing(self):
        self.is_running = False
        try:
            if self.fish_bite_detector.audio_thread is not None:
                while self.fish_bite_detector.audio_thread.is_alive():
                    time.sleep(0.1)  # Wait for the audio detection thread to stop
        except AttributeError:
            pass

    def game_recognition_loop(self):
        while self.is_running:
            if keyboard.is_pressed('esc'):
                print("ESC key pressed. Stopping fishing bot.")
                self.stop_fishing()
                break

            frame = self.capture_game_region()  # Use the custom method to capture the specific region
            if frame is None:
                print("Failed to capture the game screen.")
                continue

            predicted_tension = self.predict_tension(frame)
            print(f"Predicted tension: {predicted_tension}")  # Print the predicted tension every second

            if predicted_tension == "low":
                self.game_interaction.press_key("s")
            elif predicted_tension == "high":
                self.game_interaction.release_key("s")
                time.sleep(3)  # Wait for 3 seconds before pressing "s" again
                self.game_interaction.press_key("s")

            caught_fish = self.is_fish_caught(frame)  # Pass the captured frame to is_fish_caught()
            if caught_fish:
                print(f"Congratulations! You caught a {caught_fish}!")
                break

            time.sleep(1)  # Predict the tension every second
            
    def is_fish_caught(self, frame):
        try:
            caught_fish = self.fish_caught_detector.is_fish_caught(frame)
            if caught_fish:
                return caught_fish
        except Exception as e:
            pass
        
        return None
    
    def capture_game_region(self):
        with mss() as sct:
            # Get the primary monitor dimensions
            monitor = sct.monitors[0]
            monitor_width = monitor['width']
            monitor_height = monitor['height']

            # Calculate the actual pixel values based on percentages
            recording_x = int(monitor_width * 31 / 100)
            recording_y = int(monitor_height * 0 / 100)
            recording_width = int(monitor_width * 27.2 / 100)
            recording_height = int(monitor_height * 56 / 100)

            # Capture the screen region
            screen = sct.grab({'left': recording_x, 'top': recording_y, 
            'width': recording_width, 'height': recording_height})
            frame = np.array(screen)

            return frame