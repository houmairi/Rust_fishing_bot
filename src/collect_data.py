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
        self.video_writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, self.resolution)
        logger.info(f"Recording started. Saving to: {self.output_path}")

    def stop_recording(self):
        self.recording = False
        self.video_writer.release()
        logger.info("Recording stopped.")

    def record_frame(self):
        if self.recording:
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                left, top, right, bottom = self.crop_percentages
                crop_left = int(monitor["width"] * left / 100)
                crop_top = int(monitor["height"] * top / 100)
                crop_right = int(monitor["width"] * (1 - right / 100))
                crop_bottom = int(monitor["height"] * (1 - bottom / 100))

                logger.info(f"Crop coordinates: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")

                frame = np.array(sct.grab({
                    "left": crop_left,
                    "top": crop_top,
                    "width": crop_right - crop_left,
                    "height": crop_bottom - crop_top
                }))

                logger.info(f"Captured frame shape: {frame.shape}")

                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, self.resolution, interpolation=cv2.INTER_LINEAR)

                logger.info(f"Resized frame shape: {frame.shape}")

                self.video_writer.write(frame)

def on_press(key):
    global recorder
    if key == keyboard.KeyCode.from_char('p'):
        if not recorder.recording:
            recorder.start_recording()
        else:
            recorder.stop_recording()
            return False

def main():
    output_dir = "screen_recordings"
    os.makedirs(output_dir, exist_ok=True)

    fps = 30.0
    resolution = (1920, 1080)
    crop_percentages = (10, 20, 5, 15)  # Left, Top, Right, Bottom

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"screen_recording_{timestamp}.mp4")

    global recorder
    recorder = ScreenRecorder(output_path, fps=fps, resolution=resolution, crop_percentages=crop_percentages)

    logger.info("Press 'p' to start/stop the recording.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    while recorder.recording:
        recorder.record_frame()

if __name__ == "__main__":
    main()