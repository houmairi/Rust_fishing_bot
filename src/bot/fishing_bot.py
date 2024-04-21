import sys
import os
import time
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from src.sound.sound_detection import FishBiteDetector
from src.bot.fish_caught_detector import FishCaughtDetector
import keyboard

class FishingBot:
    def __init__(self, game_interaction, reference_images_path):
        self.game_interaction = game_interaction
        self.fish_bite_detector = FishBiteDetector()
        self.fish_bite_detector.on_sound_cue_recognized = self.on_fish_bite_detected
        self.is_running = False
        self.fish_caught_detector = FishCaughtDetector(reference_images_path)

    def start_fishing(self):
        self.is_running = True
        print("Fishing bot started. Press 'Esc' to stop.")
        #self.game_interaction.start_game()
        self.game_recognition_loop()
        self.fish_bite_detector.start_detection()

        while True:
            caught_fish = self.is_fish_caught()
            if caught_fish:
                print(f"Congratulations! You caught a {caught_fish}!")
                break
            time.sleep(1)  # Wait before checking again

        print("Fishing bot stopped.")
        self.stop_fishing()

    def on_fish_bite_detected(self, similarity):
        if self.is_running and similarity >= 0.8:
            self.game_interaction.perform_action("press_s")
            print("Fish bite detected. Pressing 'S' to start fishing minigame.")

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
        # Capture the game screen
        screen_image = self.game_interaction.capture_game_screen()
        
        # Check if a fish is caught using the FishCaughtDetector
        caught_fish = self.fish_caught_detector.is_fish_caught(screen_image)
        
        return caught_fish