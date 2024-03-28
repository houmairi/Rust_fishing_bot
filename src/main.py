import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.bot.fishing_bot import FishingBot
from src.bot.game_interaction import GameInteraction

def main():
    game_window_title = "Rust"
    game_interaction = GameInteraction(game_window_title)
    fishing_bot = FishingBot(game_interaction)
    try:
        fishing_bot.start_fishing()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping fishing bot.")
    finally:
        fishing_bot.stop_fishing()

if __name__ == "__main__":
    main()