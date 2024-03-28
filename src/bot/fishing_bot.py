import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from src.sound.sound_detection import FishBiteDetector
import keyboard

class FishingBot:
    def __init__(self, game_interaction):
        self.game_interaction = game_interaction
        self.fish_bite_detector = FishBiteDetector()
        self.fish_bite_detector.on_sound_cue_recognized = self.on_fish_bite_detected
        self.is_running = False

    def start_fishing(self):
        self.is_running = True
        print("Fishing bot started. Press 'Esc' to stop.")
        self.game_interaction.start_game()
        self.fish_bite_detector.start_detection()
        self.game_recognition_loop()

    def on_fish_bite_detected(self, similarity):
        if self.is_running and similarity >= 0.8:
            #self.game_interaction.perform_action("press_s")
            print("test")

    def stop_fishing(self):
        self.is_running = False
        self.fish_bite_detector.stop_detection()
        while self.fish_bite_detector.audio_thread.is_alive():
            time.sleep(0.1)  # Wait for the audio detection thread to stop
        self.game_interaction.stop_game()

    def game_recognition_loop(self):
        while self.is_running:
            if keyboard.is_pressed('esc'):
                print("ESC key pressed. Stopping fishing bot.")
                self.stop_fishing()
                break