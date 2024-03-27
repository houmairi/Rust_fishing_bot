import sys
import os
import time
from threading import Event
import keyboard
import wave

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

    output_file = "recorded_audio.wav"
    print("Starting audio detection...")
    fish_bite_detector.start_detection(device_index, output_file)

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
    print("Press 'Esc' to stop audio detection and save the recorded audio.")

    # Wait for a specific duration (e.g., 10 seconds) before stopping the audio detection
    time.sleep(10)

    fish_bite_detector.stop_detection()
    print("Audio detection stopped. Saving recorded audio...")

    print(f"Recorded audio saved to: {output_file}")

if __name__ == "__main__":
    main()