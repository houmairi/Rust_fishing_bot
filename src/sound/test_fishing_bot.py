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
    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector()

    print("Recording the first 10 seconds of audio...")
    fish_bite_detector.record_audio(duration=10, output_file="recorded_audio.wav")

    print("Starting audio detection...")
    fish_bite_detector.start_detection()

    # Create an event to signal when the sound cue is recognized
    sound_cue_recognized = Event()

    # Function to be called when the sound cue is recognized
    def on_sound_cue_recognized():
        sound_cue_recognized.set()
        print("Sound cue recognized! Fishing minigame started.")
        #game_interaction.perform_action("press_s")

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
    print("Press 'Ctrl+C' to stop audio detection.")

    try:
        while True:
            time.sleep(1)  # Keep the main thread running
    except KeyboardInterrupt:
        print("Stopping audio detection...")
        fish_bite_detector.stop_detection()

if __name__ == "__main__":
    main()