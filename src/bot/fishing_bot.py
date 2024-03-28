import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from src.bot.game_interaction import GameInteraction
from src.ml.model_training import train_model
from src.video.video_processing import detect_fish_movement, detect_rod_shake
from src.sound.sound_detection import FishBiteDetector

class FishingBot:
    def __init__(self):
        self.game_interaction = GameInteraction()
        self.fish_bite_detector = FishBiteDetector()
        self.fish_bite_detector.on_sound_cue_recognized = self.on_fish_bite_detected

    def start_fishing(self):
        self.game_interaction.start_game()
        self.fish_bite_detector.start_detection()

    def on_fish_bite_detected(self):
        self.game_interaction.perform_action("press_s")

    def stop_fishing(self):
        self.fish_bite_detector.stop_detection()
        self.game_interaction.stop_game()