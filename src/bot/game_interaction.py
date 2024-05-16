import pyautogui
import time
import win32gui
import numpy as np

class GameInteraction:
    def __init__(self, game_window_title=None):
        self.game_window_title = game_window_title

    def is_game_running(self):
        if self.game_window_title is None:
            return True

        # Get the list of window titles
        window_titles = pyautogui.getAllTitles()

        # Check if the game window title exists in the list of window titles
        if self.game_window_title in window_titles:
            return True
        else:
            return False

    def focus_game_window(self):
        if self.game_window_title is None:
            return

        # Find the game window by its title
        game_window = win32gui.FindWindow(None, self.game_window_title)

        if game_window:
            # Bring the game window to the foreground
            win32gui.SetForegroundWindow(game_window)
            time.sleep(0.5)  # Wait for the window to be activated
        else:
            raise Exception("Game window not found.")

    def press_key(self, key):
        self.focus_game_window()
        pyautogui.keyDown(key)

    def release_key(self, key):
        self.focus_game_window()
        pyautogui.keyUp(key)

    def start_game(self):
        print("Waiting for the game to start...")
        while True:
            if self.is_game_running():
                print("Game recognized. Starting fishing.")
                break
            time.sleep(1)

    def stop_game(self):
        print("Stopping the game...")
        
        # Bring the game window to the foreground
        self.focus_game_window()
        
        # Send the key combination to close the game window
        pyautogui.hotkey('alt', 'f4')
        
        # Wait for the game window to close
        while self.is_game_running():
            time.sleep(1)
        
        print("Game stopped.")

    def capture_game_screen(self):
        self.focus_game_window()
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        return screen_np