import sys
import os
import time
from threading import Event

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.bot.fishing_bot import FishingBot
from src.bot.game_interaction import GameInteraction
from src.sound.sound_detection import FishBiteDetector

def main():
    global sound_cue_recognized  # Declare sound_cue_recognized as a global variable

    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fishing_bot = FishingBot(game_interaction)
    fish_bite_detector = FishBiteDetector()

    # Prompt the user for sound recognition preference
    while True:
        user_input = input("Do you want to start sound recognition immediately? (y/n): ")
        if user_input.lower() == 'y':
            start_sound_recognition = True
            break
        elif user_input.lower() == 'n':
            start_sound_recognition = False
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    if start_sound_recognition:
        print("Starting audio detection...")
        fish_bite_detector.start_detection()
    else:
        print("Waiting for the game to be recognized...")

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
        if not start_sound_recognition:
            while True:
                if game_interaction.is_game_running():
                    print("Rust game detected!")
                    print("Starting audio detection...")
                    fish_bite_detector.start_detection()
                    fishing_bot.start_fishing()
                    break
                else:
                    print("Rust game not found. Waiting...")
                    time.sleep(5)  # Wait for 5 seconds before checking again

        print("Waiting for the sound cue to be recognized...")
        print("Press 'Ctrl+C' to stop the fishing bot.")

        while True:
            time.sleep(1)  # Keep the main thread running
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