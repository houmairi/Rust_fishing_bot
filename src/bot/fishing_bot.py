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

class FishingBot:
    def __init__(self, game_interaction):
        self.game_interaction = GameInteraction()
        self.fish_bite_detector = FishBiteDetector()
        #self.fish_bite_detector.on_sound_cue_recognized = self.on_fish_bite_detected
        self.is_running = False
        self.fish_caught_detector = FishCaughtDetector()  # Remove the reference_images_path argument

    def start_fishing(self):
        self.is_running = True
        print("Fishing bot started. Press 'Esc' to stop.")
        self.game_recognition_loop()
        
        # Stop the sound detection when the minigame starts
        self.fish_bite_detector.stop_detection()
        
        #caught_fish = self.is_fish_caught()
        #if caught_fish:
        #    print(f"Congratulations! You caught a {caught_fish}!")
        #else:
        #    print("No fish caught.")
        
        self.stop_fishing()

    def stop_fishing(self):
        self.is_running = False
        try:
            if self.fish_bite_detector.audio_thread is not None:
                while self.fish_bite_detector.audio_thread.is_alive():
                    time.sleep(0.1)  # Wait for the audio detection thread to stop
        except AttributeError:
            pass
        #self.game_interaction.stop_game()  # Call the stop_game method

    def game_recognition_loop(self):
        while self.is_running:
            if keyboard.is_pressed('esc'):
                print("ESC key pressed. Stopping fishing bot.")
                self.stop_fishing()
                break
            
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