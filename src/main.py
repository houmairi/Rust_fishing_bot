import sys
import os
import time
from threading import Event

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

#from bot.fish_caught_detector import FishCaughtDetector
from src.bot.fishing_bot import FishingBot
from src.bot.game_interaction import GameInteraction
from src.sound.sound_detection import FishBiteDetector

def main():
    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector()
    fishing_bot = FishingBot(game_interaction)
    
    model_path = "ml/labeled_data/iteration_20240518_141944/trained_model.keras"
    label_encoder_path = "ml/labeled_data/iteration_20240518_141944/label_encoder.pkl"
    fishing_bot.load_model(model_path, label_encoder_path)

    is_fishing_active = False

    def on_sound_cue_recognized(similarity):
        nonlocal is_fishing_active
        if not is_fishing_active:
            print(f"Sound cue recognized with similarity: {similarity:.2f}! Fishing minigame started.")
            is_fishing_active = True
            fish_bite_detector.stop_detection()  # Stop sound detection during the minigame
            try:
                fishing_bot.start_fishing()  # Start the fishing bot when the sound cue is recognized

                start_time = time.time()
                timeout = 20  # Maximum time to scan for a fish caught (in seconds)

                print("Starting OCR")
                while time.time() - start_time < timeout:
                    caught_fish = fishing_bot.is_fish_caught()
                    if caught_fish:
                        print(f"Congratulations! You caught a {caught_fish}!")
                        break
                    time.sleep(0.1)  # Add a small delay between each scan

                if not caught_fish:
                    print("It seems like no fish was caught.")

                fishing_bot.stop_fishing()
                is_fishing_active = False
                print("Sound cue recognition will repeat.")
                fish_bite_detector.start_detection()  # Restart sound detection after the minigame ends
            except Exception as e:
                print(f"An error occurred during the fishing process: {str(e)}")
                fishing_bot.stop_fishing()
                is_fishing_active = False
                print("Sound cue recognition will repeat.")
                fish_bite_detector.start_detection()  # Restart sound detection after the minigame ends

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