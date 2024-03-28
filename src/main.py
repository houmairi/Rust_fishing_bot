import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.bot.fishing_bot import FishingBot

def main():
    fishing_bot = FishingBot()
    fishing_bot.start_fishing()
    # Add any necessary cleanup or termination logic

if __name__ == "__main__":
    main()
    