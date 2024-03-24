import sys
import os

# Add the project's root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(1, project_root)

from src.bot.game_interaction import GameInteraction
from sound_detection import FishBiteDetector
import time

def main():
    game_window_title = "Rust"  # Replace with the actual game window title
    game_interaction = GameInteraction(game_window_title)
    fish_bite_detector = FishBiteDetector(game_window_title)

    while True:
        if game_interaction.is_game_running():
            print("Rust game detected!")
            break
        else:
            print("Rust game not found. Waiting...")
            time.sleep(5)  # Wait for 5 seconds before checking again

    while True:
        if fish_bite_detector.detect_fish_bite():
            print("Sound cue detected! Fishing minigame started.")
            break
        else:
            print("Waiting for fishing to start...")
            time.sleep(1)  # Wait for 1 second before checking again

if __name__ == "__main__":
    main()