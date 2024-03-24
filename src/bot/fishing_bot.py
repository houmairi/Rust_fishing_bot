import time
from src.bot.game_interaction import GameInteraction
from src.ml.model_inference import FishingPredictor
from src.sound.sound_detection import FishBiteDetector

class FishingBot:
    def __init__(self):
        self.game_interaction = GameInteraction()
        self.fishing_predictor = FishingPredictor()
        self.fish_bite_detector = FishBiteDetector()

    def start_fishing(self):
        print("Waiting for fishing to start...")
        while True:
            # Wait for a fish bite using sound detection
            while not self.fish_bite_detector.detect_fish_bite():
                time.sleep(0.1)  # Small delay to avoid excessive CPU usage

            print("Fishing minigame started!")

            # Start the fishing minigame
            while True:
                # Observe the fish movement and rod shake
                fish_movement, rod_shake = self.game_interaction.observe_fishing_state()

                # Predict the appropriate counter-movement using the ML model
                counter_movement = self.fishing_predictor.predict(fish_movement, rod_shake)

                # Perform the counter-movement in the game
                self.game_interaction.perform_action(counter_movement)

                # Check if the fish is caught or unhooked
                if self.game_interaction.is_fish_caught():
                    break
                elif self.game_interaction.is_fish_unhooked():
                    break

            # Small delay before checking for the next fishing spot
            time.sleep(1)