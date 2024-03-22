import pyautogui
import time
import mss
import numpy as np
import win32gui

class GameInteraction:
    def __init__(self, game_window_title):
        self.game_window_title = game_window_title
        self.sct = mss.mss()

    def focus_game_window(self):
        # Find the game window by its title
        game_window = win32gui.FindWindow(None, self.game_window_title)

        if game_window:
            # Bring the game window to the foreground
            win32gui.SetForegroundWindow(game_window)
            time.sleep(0.5)  # Wait for the window to be activated
        else:
            raise Exception("Game window not found.")

    def move_to_fishing_spot(self, spot_coordinates):
        self.focus_game_window()
        # Move the mouse to the specified fishing spot coordinates
        pyautogui.moveTo(spot_coordinates[0], spot_coordinates[1])

    def cast_fishing_line(self):
        self.focus_game_window()
        # Perform the action to cast the fishing line
        pyautogui.click(button='right')

    def observe_fishing_state(self):
        self.focus_game_window()
        # Capture the relevant region of the game screen
        screen_region = {'top': 100, 'left': 100, 'width': 800, 'height': 600}
        screen_image = np.array(self.sct.grab(screen_region))

        # Process the screen image to extract fish movement and rod shake information
        fish_movement = self._detect_fish_movement(screen_image)
        rod_shake = self._detect_rod_shake(screen_image)

        return fish_movement, rod_shake

    def perform_action(self, counter_movement):
        self.focus_game_window()
        # Map the counter-movement to the corresponding key press or mouse action
        if counter_movement == 0:
            pyautogui.keyDown('a')  # Move left
        elif counter_movement == 1:
            pyautogui.keyDown('d')  # Move right
        elif counter_movement == 2:
            pyautogui.keyDown('w')  # Move up
        elif counter_movement == 3:
            pyautogui.keyDown('s')  # Move down

        # Release the key after a short delay
        time.sleep(0.1)
        pyautogui.keyUp('a')
        pyautogui.keyUp('d')
        pyautogui.keyUp('w')
        pyautogui.keyUp('s')

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