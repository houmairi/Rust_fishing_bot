import cv2
import numpy as np
from mss import mss

def main():
    # Specify the screen recording size and location using percentages
    recording_x_percent = 31  # Adjust the x-coordinate percentage of the top-left corner
    recording_y_percent = 0  # Adjust the y-coordinate percentage of the top-left corner
    recording_width_percent = 27.2  # Adjust the width percentage of the captured region
    recording_height_percent = 56  # Adjust the height percentage of the captured region

    with mss() as sct:
        # Get the primary monitor dimensions
        monitor = sct.monitors[0]
        monitor_width = monitor['width']
        monitor_height = monitor['height']

        # Calculate the actual pixel values based on percentages
        recording_x = int(monitor_width * recording_x_percent / 100)
        recording_y = int(monitor_height * recording_y_percent / 100)
        recording_width = int(monitor_width * recording_width_percent / 100)
        recording_height = int(monitor_height * recording_height_percent / 100)

        while True:
            # Capture the screen region
            screen = sct.grab({'left': recording_x, 'top': recording_y, 'width': recording_width, 'height': recording_height})
            frame = np.array(screen)

            # Display the captured frame
            cv2.imshow('Captured Region', frame)
            # Check for 'q' key press to quit the program
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()