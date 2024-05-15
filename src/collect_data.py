import cv2
import numpy as np
import time
import os
from pynput import keyboard
import mss
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScreenRecorder:
    def __init__(self, output_path, fps=30.0, resolution=(1920, 1080), crop_percentages=(0, 0, 0, 0)):
        self.output_path = output_path
        self.fps = fps
        self.resolution = resolution
        self.crop_percentages = crop_percentages
        self.recording = False
        self.video_writer = None

    def start_recording(self):
        self.recording = True
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # Get the dimensions of the cropped region
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Change the index to select the desired monitor
            left, top, right, bottom = self.crop_percentages

            # Calculate crop coordinates relative to the selected monitor
            crop_left = int(monitor["width"] * left / 100)
            crop_top = int(monitor["height"] * top / 100)
            crop_right = int(monitor["width"] * (100 - right) / 100)
            crop_bottom = int(monitor["height"] * (100 - bottom) / 100)

            # Ensure crop coordinates are within valid range
            crop_left = max(0, min(crop_left, monitor["width"]))
            crop_top = max(0, min(crop_top, monitor["height"]))
            crop_right = max(crop_left, min(crop_right, monitor["width"]))
            crop_bottom = max(crop_top, min(crop_bottom, monitor["height"]))

            # Calculate the dimensions of the cropped region
            cropped_width = crop_right - crop_left
            cropped_height = crop_bottom - crop_top

        # Set the video writer's dimensions to the cropped region's dimensions
        self.video_writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, (cropped_width, cropped_height))
        logger.info(f"Recording started. Saving to: {self.output_path}")

    def stop_recording(self):
        self.recording = False
        self.video_writer.release()
        logger.info("Recording stopped.")

    def record_frame(self):
        with mss.mss() as sct:
            # Get the monitor to capture (assuming you want to capture the primary monitor)
            monitor = sct.monitors[1]  # Change the index to select the desired monitor

            left, top, right, bottom = self.crop_percentages

            # Calculate crop coordinates relative to the selected monitor
            crop_left = int(monitor["width"] * left / 100)
            crop_top = int(monitor["height"] * top / 100)
            crop_right = int(monitor["width"] * (100 - right) / 100)
            crop_bottom = int(monitor["height"] * (100 - bottom) / 100)

            # Ensure crop coordinates are within valid range
            crop_left = max(0, min(crop_left, monitor["width"]))
            crop_top = max(0, min(crop_top, monitor["height"]))
            crop_right = max(crop_left, min(crop_right, monitor["width"]))
            crop_bottom = max(crop_top, min(crop_bottom, monitor["height"]))

            logger.info(f"Crop coordinates: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")

            frame = np.array(sct.grab({
                "left": monitor["left"] + crop_left,
                "top": monitor["top"] + crop_top,
                "width": crop_right - crop_left,
                "height": crop_bottom - crop_top
            }))

            logger.info(f"Captured frame shape: {frame.shape}")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            self.video_writer.write(frame)

def on_press(key):
    global recorder, running
    if key == keyboard.KeyCode.from_char('p'):
        if not recorder.recording:
            recorder.start_recording()
        else:
            recorder.stop_recording()
            running = False
            return False

def main():
    output_dir = "screen_recordings"
    os.makedirs(output_dir, exist_ok=True)

    fps = 30.0
    resolution = (2560, 1440)
    crop_percentages = (50, 15, 20, 0)  # Left, Top, Right, Bottom

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"screen_recording_{timestamp}.mp4")

    global recorder, running
    recorder = ScreenRecorder(output_path, fps=fps, resolution=resolution, crop_percentages=crop_percentages)
    running = True

    logger.info("Press 'p' to start/stop the recording.")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while running:
        if recorder.recording:
            recorder.record_frame()
        time.sleep(1 / fps)

    listener.stop()

if __name__ == "__main__":
    main()