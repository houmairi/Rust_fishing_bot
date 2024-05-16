import cv2
import numpy as np
import time
import os
from pynput import keyboard
import mss
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScreenRecorder:
    def __init__(self, output_path, fps=30.0, resolution=(1920, 1080), crop_percentages=(0, 0, 0, 0)):
        self.output_path = output_path
        self.fps = fps
        self.resolution = resolution
        self.crop_percentages = crop_percentages
        self.recording = False
        self.video_writer = None
        self.frame_counter = 0
        self.start_time = 0
        self.time_per_frame = 1 / self.fps  # Time per frame in seconds

    def start_recording(self):
        self.recording = True
        self.frame_counter = 0
        self.start_time = time.time()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

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
        
        # Check if the video writer is initialized successfully
        if not self.video_writer.isOpened():
            logger.error("Failed to initialize VideoWriter. Please check codec configuration and library dependencies.")
            self.recording = False
            return

        logger.info(f"Recording started. Saving to: {self.output_path}")
        logger.info(f"VideoWriter FPS set to: {self.fps}")

    def stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
        self.recording = False
        logger.info("Recording stopped.")
        logger.info(f"Total frames recorded: {self.frame_counter}")
        logger.info(f"Actual recording duration: {time.time() - self.start_time:.2f} seconds")

    def record_frame(self):
        if not self.recording or self.video_writer is None:
            return

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

            frame = np.array(sct.grab({
                "left": monitor["left"] + crop_left,
                "top": monitor["top"] + crop_top,
                "width": crop_right - crop_left,
                "height": crop_bottom - crop_top
            }))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            self.video_writer.write(frame)
            self.frame_counter += 1

            logger.debug(f"Frame {self.frame_counter} captured and written.")

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
    output_path = os.path.join(output_dir, f"screen_recording_{timestamp}.avi")  # Changed to .avi for XVID codec

    global recorder, running
    recorder = ScreenRecorder(output_path, fps=fps, resolution=resolution, crop_percentages=crop_percentages)
    running = True

    logger.info("Press 'p' to start/stop the recording.")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    frame_time_start = None

    while running:
        if recorder.recording:
            if frame_time_start is None:
                frame_time_start = time.time()

            recorder.record_frame()
            frame_time_start += recorder.time_per_frame
            time_to_sleep = frame_time_start - time.time()
            
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
            else:
                logger.warning("Frame processing is taking longer than expected.")

    listener.stop()

if __name__ == "__main__":
    main()
