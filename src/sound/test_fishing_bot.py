import sys
import os
import time
from threading import Event

# Add the project's root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(1, project_root)

from src.bot.game_interaction import GameInteraction
from sound_detection import FishBiteDetector

def main():
    game_window_title = "Rust"  # Replace with the actual game window title
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector(game_window_title)
    
    print("Listing available audio devices...")
    fish_bite_detector.list_audio_devices()

    # Get the desired device index from user input
    device_index = int(input("Enter the device index to use for audio detection: "))

    print("Starting audio detection...")
    fish_bite_detector.start_detection(device_index)

    # Create an event to signal when the sound cue is recognized
    sound_cue_recognized = Event()

    # Function to be called when the sound cue is recognized
    def on_sound_cue_recognized():
        sound_cue_recognized.set()
        print("Sound cue recognized! Fishing minigame started.")

    # Register the callback function in the FishBiteDetector
    fish_bite_detector.on_sound_cue_recognized = on_sound_cue_recognized

    while True:
        if game_interaction.is_game_running():
            print("Rust game detected!")
            break
        else:
            print("Rust game not found. Waiting...")
            time.sleep(5)  # Wait for 5 seconds before checking again

    print("Waiting for the sound cue to be recognized...")
    sound_cue_recognized.wait()  # Wait until the sound cue is recognized

    print("Sound cue recognized! Fishing minigame started.")

    # Perform actions after the sound cue is recognized
    # ...

    input("Press Enter to stop audio detection and exit...")
    fish_bite_detector.stop_detection()

if __name__ == "__main__":
    main()