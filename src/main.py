import sys
import os
import time
from threading import Event

# Add the project's root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from bot.game_interaction import GameInteraction
from bot.fishing_bot import FishingBot
from sound.sound_detection import FishBiteDetector

def main():
    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector()
    fishing_bot = FishingBot(game_interaction)

    # Load the trained model and label encoder
    #model_path = "ml/data2process/iteration_20240505_123552/trained_model.pkl"  # Replace with the actual path
    #label_encoder_path = "ml/data2process/iteration_20240505_123552/label_encoder.pkl"  # Replace with the actual path
    #fishing_bot.load_model(model_path, label_encoder_path)

    # Create an event to signal when the sound cue is recognized
    sound_cue_recognized = Event()

    def on_sound_cue_recognized(similarity):
        sound_cue_recognized.set()
        print(f"Sound cue recognized! Similarity: {similarity:.2f}. Fishing minigame started.")
        try:
            fishing_bot.start_fishing()
        except Exception as e:
            print(f"An error occurred during the fishing process: {str(e)}")
            fishing_bot.stop_fishing()

    fish_bite_detector.on_sound_cue_recognized = on_sound_cue_recognized

    try:
        while True:
            if game_interaction.is_game_running():
                print("Rust game detected!")
                print("Starting audio detection...")
                fish_bite_detector.start_detection()
                print("Audio detection started. Waiting for a fish bite...")

                # Wait for the sound cue to be recognized
                sound_cue_recognized.wait()

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