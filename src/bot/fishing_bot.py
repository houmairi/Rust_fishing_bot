import sys
import os
import time
from pytesseract import TesseractNotFoundError
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from src.sound.sound_detection import FishBiteDetector
from src.bot.fish_caught_detector import FishCaughtDetector
from src.bot.game_interaction import GameInteraction  # Import the GameInteraction class
import keyboard
import joblib
import cv2
import numpy as np

class FishingBot:
    def __init__(self, game_interaction):
        self.game_interaction = GameInteraction()
        self.fish_bite_detector = FishBiteDetector()
        self.is_running = False
        self.fish_caught_detector = FishCaughtDetector()
        self.model = None
        self.label_encoder = None

    def load_model(self, model_path, label_encoder_path):
        self.model = joblib.load(model_path)
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, frame):
        # Preprocess the frame
        preprocessed_frame = self.preprocess_frame(frame)

        # Make predictions using the loaded model
        predicted_label_encoded = self.model.predict([preprocessed_frame])
        predicted_label = self.label_encoder.inverse_transform(predicted_label_encoded)[0]

        return predicted_label

    def preprocess_frame(self, frame):
        # Resize the frame to 800x600
        resized_frame = cv2.resize(frame, (2560, 1440))

        # Convert the frame to grayscale if needed
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        # Flatten the frame to a 1D array
        flattened_frame = gray_frame.flatten()

        return flattened_frame

    def start_fishing(self):
        self.is_running = True
        print("Fishing bot started. Press 'Esc' to stop.")
        self.game_recognition_loop()
        
        # Stop the sound detection when the minigame starts
        self.fish_bite_detector.stop_detection()
        
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

            # Capture the game screen
            frame = self.game_interaction.capture_game_screen()

            if frame is None:
                print("Failed to capture the game screen.")
                continue

            # Make predictions using the loaded model
            predicted_label = self.predict(frame)

            # Perform actions based on the predicted label
            if predicted_label == "Fish moves to the left":
                self.game_interaction.perform_action("press_d")
            elif predicted_label == "Fish moves to the right":
                self.game_interaction.perform_action("press_a")
            # Add more conditions for other labels and corresponding actions

            # Check if a fish is caught using OCR
            caught_fish = self.is_fish_caught()
            if caught_fish:
                print(f"Congratulations! You caught a {caught_fish}!")
                break

            # Add a small delay between each iteration
            time.sleep(0.1)
        
    def is_fish_caught(self):
        start_time = time.time()
        timeout = 15  # Maximum time to scan for a fish caught (in seconds)
        
        while time.time() - start_time < timeout:
            # Capture the game screen
            screen_image = self.game_interaction.capture_game_screen()
            
            if screen_image is None:
                print("Failed to capture the game screen.")
                return None
            
            try:
                # Check if a fish is caught using the FishCaughtDetector
                caught_fish = self.fish_caught_detector.is_fish_caught(screen_image)
                if caught_fish:
                    return caught_fish
            except Exception as e:
                print(f"An error occurred during the OCR process: {str(e)}")
            
            # Add a small delay between each scan
            time.sleep(0.1)
        
        # If no fish is caught within the timeout, return None
        return None