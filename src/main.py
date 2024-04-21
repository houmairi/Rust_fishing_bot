import sys
import os
import time
from threading import Event

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from bot.fish_caught_detector import FishCaughtDetector
from src.bot.fishing_bot import FishingBot
from src.bot.game_interaction import GameInteraction
from src.sound.sound_detection import FishBiteDetector

def main():
    global sound_cue_recognized  # Declare sound_cue_recognized as a global variable

    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector()
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    reference_images_path = os.path.join(project_root,"rust-fishing-bot" ,"data", "fishing_data", "fishing_caught_images")
    fishing_bot = FishingBot(game_interaction, reference_images_path)

    # Create an event to signal when the sound cue is recognized
    sound_cue_recognized = Event()

    # Function to be called when the sound cue is recognized
    def on_sound_cue_recognized(similarity):
        sound_cue_recognized.set()
        print(f"Sound cue recognized with similarity: {similarity:.2f}! Fishing minigame started.")
        fishing_bot.on_fish_bite_detected(similarity)

    # Register the callback function in the FishBiteDetector
    fish_bite_detector.on_sound_cue_recognized = on_sound_cue_recognized

    try:
        while True:
            if game_interaction.is_game_running():
                print("Rust game detected!")
                print("Starting audio detection...")
                fish_bite_detector.start_detection()
                print("Audio detection started. Waiting for a fish bite...")
                sound_cue_recognized.wait()  # Wait for the sound cue to be recognized
                fishing_bot.start_fishing()  # Start fishing after the sound cue is recognized
                while True:
                    caught_fish = fishing_bot.is_fish_caught()
                    if caught_fish:
                        print(f"Congratulations! You caught a {caught_fish}!")
                        break
                    time.sleep(1)  # Wait before checking again
                break
            else:
                print("Rust game not found. Waiting...")
                time.sleep(5)  # Wait for 5 seconds before checking again

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping fishing bot.")
    except AttributeError as e:
        print(f"AttributeError occurred: {str(e)}")
    finally:
        try:
            fishing_bot.stop_fishing()
            fish_bite_detector.stop_detection()
        except AttributeError:
            pass

if __name__ == "__main__":
    main()