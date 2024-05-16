import sys
import os
import time
from threading import Event
import threading
import cv2
import numpy as np
import joblib
from mss import mss

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.bot.fishing_bot import FishingBot
from src.bot.game_interaction import GameInteraction
from src.sound.sound_detection import FishBiteDetector

def preprocess_image(image):
    preprocessed_image = cv2.resize(image, (320, 420))  # Adjust the size to match the training preprocessing
    preprocessed_image = cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2GRAY)
    preprocessed_image = preprocessed_image.flatten()  # Flatten the image
    return preprocessed_image

def predict_label(model, image):
    preprocessed_image = preprocess_image(image)
    predicted_label = model.predict([preprocessed_image])
    return predicted_label[0]

def main():
    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector()
    fishing_bot = FishingBot(game_interaction)

    # Load the trained model and label encoder
    model_directory = 'C:/Users/Niko/Documents/Repositorys/rust-fishing-bot/src/ml/labeled_data/iteration_20240516_130408'
    model_path = os.path.join(model_directory, 'trained_model.pkl')
    label_encoder_path = os.path.join(model_directory, 'label_encoder.pkl')
    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)

    # Specify the screen recording size and location using percentages
    recording_x_percent = 31  # Adjust the x-coordinate percentage of the top-left corner
    recording_y_percent = 0  # Adjust the y-coordinate percentage of the top-left corner
    recording_width_percent = 27.2  # Adjust the width percentage of the captured region
    recording_height_percent = 56  # Adjust the height percentage of the captured region

    def on_sound_cue_recognized(similarity):
        print(f"Sound cue recognized with similarity: {similarity:.2f}! Fishing minigame started.")

        # Create a stop event for the prediction loop
        stop_event = threading.Event()

        def prediction_loop():
            try:
                with mss() as sct:
                    # Get the primary monitor dimensions
                    monitor = sct.monitors[0]
                    monitor_width = monitor['width']
                    monitor_height = monitor['height']

                    # Calculate the actual pixel values based on percentages
                    recording_x = int(monitor_width * recording_x_percent / 100)
                    recording_y = int(monitor_height * recording_y_percent / 100)
                    recording_width = int(monitor_width * recording_width_percent / 100)
                    recording_height = int(monitor_height * recording_height_percent / 100)

                    print("Starting fishing rod recognition")
                    while not stop_event.is_set():
                        # Capture the screen region
                        screen = sct.grab({'left': recording_x, 'top': recording_y, 'width': recording_width, 'height': recording_height})
                        frame = np.array(screen)

                        # Predict the tension state
                        predicted_label_encoded = predict_label(model, frame)
                        predicted_label = label_encoder.inverse_transform([predicted_label_encoded])[0]

                        # Print the recognized tension state
                        print(f"Rod state: {predicted_label}")

                        if predicted_label == 'low':
                            game_interaction.press_key('S')
                        elif predicted_label == 'high':
                            game_interaction.release_key('S')
                            time.sleep(0.1)  # Reduce the wait time for faster response

                        time.sleep(0.1)  # Reduce the delay between predictions for faster response
            except Exception as e:
                print(f"An error occurred during the fishing process: {str(e)}")

        # Start the prediction loop in a separate thread
        prediction_thread = threading.Thread(target=prediction_loop)
        prediction_thread.start()

        try:
            start_time = time.time()
            timeout = 25  # Maximum time for the fishing minigame (in seconds)

            while time.time() - start_time < timeout:
                caught_fish = fishing_bot.is_fish_caught()
                if caught_fish:
                    print(f"Congratulations! You caught a {caught_fish}!")
                    break

                time.sleep(0.5)  # Add a small delay between each OCR check

            if not caught_fish:
                print("It seems like no fish was caught.")
        except Exception as e:
            print(f"An error occurred during the OCR process: {str(e)}")
        finally:
            # Stop the prediction loop
            stop_event.set()
            prediction_thread.join()

        fishing_bot.stop_fishing()
        print("Sound cue recognition will repeat.")

    fish_bite_detector.on_sound_cue_recognized = on_sound_cue_recognized

    try:
        while True:
            if game_interaction.is_game_running():
                print("Rust game detected!")
                print("Starting audio detection...")
                fish_bite_detector.start_detection()
                print("Audio detection started. Waiting for a fish bite...")

                while True:
                    time.sleep(1)  # Wait for 1 second before checking again

            else:
                print("Rust game not found. Waiting...")
                time.sleep(5)  # Wait for 5 seconds before checking again

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping fishing bot.")
    finally:
        try:
            fishing_bot.stop_fishing()
            fish_bite_detector.stop_detection()
        except AttributeError:
            pass

if __name__ == "__main__":
    main()