import pyautogui
import time
import mss
import mss.tools
import numpy as np
import win32gui
from pynput.keyboard import Controller as KeyboardController, Key

class GameInteraction:
    def __init__(self, game_window_title=None):
        self.game_window_title = game_window_title
        self.sct = mss.mss()
        self.keyboard = KeyboardController()

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

    def capture_game_screen(self):
        if self.game_window_title is None:
            return pyautogui.screenshot()

        window_handle = win32gui.FindWindow(None, self.game_window_title)
        if window_handle == 0:
            return None

        window_rect = win32gui.GetWindowRect(window_handle)
        monitor = {"top": window_rect[1], "left": window_rect[0], "width": window_rect[2] - window_rect[0], "height": window_rect[3] - window_rect[1]}

        screen_shot = self.sct.grab(monitor)
        img = np.array(screen_shot)
        return img

    def focus_game_window(self):
        if self.game_window_title is None:
            return

        # Find the game window by its title
        game_window = win32gui.FindWindow(None, self.game_window_title)

        if game_window:
            # Bring the game window to the foreground
            win32gui.SetForegroundWindow(game_window)
            # time.sleep(0.5)  # Wait for the window to be activated
        else:
            raise Exception("Game window not found.")

    def start_game(self):
        print("Waiting for the game to start...")
        while True:
            if self.is_game_running():
                print("Game recognized. Starting fishing.")
                break
            time.sleep(1)

    def perform_action(self, action):
        if action == "press_s":
            self.focus_game_window()
            self.keyboard.press(Key.space)  # Press the spacebar key
            self.keyboard.release(Key.space)  # Release the spacebar key
            print("Perform action: press 's'")

    def is_fishing_finished(self):
        # Check if the fishing is finished
        # Implement the logic to detect the end of the fishing minigame
        return False

    def stop_game(self):
        # Implement the logic to stop the game
        pass

    def move_to_fishing_spot(self, spot_coordinates):
        self.focus_game_window()
        # Move the mouse to the specified fishing spot coordinates
        # pyautogui.moveTo(spot_coordinates[0], spot_coordinates[1])

    def cast_fishing_line(self):
        self.focus_game_window()
        # Perform the action to cast the fishing line
        # pyautogui.click(button='right')

    def observe_fishing_state(self):
        self.focus_game_window()
        # Capture the relevant region of the game screen
        screen_region = {'top': 100, 'left': 100, 'width': 800, 'height': 600}
        screen_image = np.array(self.sct.grab(screen_region))

        # Process the screen image to extract fish movement and rod shake information
        fish_movement = self._detect_fish_movement(screen_image)
        rod_shake = self._detect_rod_shake(screen_image)

        return fish_movement, rod_shake

    def is_fish_caught(self):
        self.focus_game_window()
        # Check if the fish is successfully caught based on game indicators
        # Implement the logic to detect if the fish is caught
        # Return True if the fish is caught, False otherwise
        return False

    def is_fish_unhooked(self):
        self.focus_game_window()
        # Check if the fish is unhooked based on game indicators
        # Implement the logic to detect if the fish is unhooked
        # Return True if the fish is unhooked, False otherwise
        return False

    def _detect_fish_movement(self, screen_image):
        # Implement the logic to detect fish movement from the screen image
        # Return the detected fish movement
        return 0

    def _detect_rod_shake(self, screen_image):
        # Implement the logic to detect rod shake from the screen image
        # Return the detected rod shake
        return 0