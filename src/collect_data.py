import cv2
import os
import time
import json
import numpy as np
from pynput import keyboard
import pyautogui
import threading

class FishingSequenceRecorder:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.out = None
        self.annotations = []
        self.start_time = 0
        self.listener = None
        self.pressed_keys = set()
        self.special_keys = set()
        self.recording = False
        self.recording_thread = None
        self.stop_event = threading.Event()
        self.rod_roi = (1199, 266, 754, 1141)  # ROI coordinates for the fishing rod
        self.prev_frame = None
        self.shake_threshold = 30  # Adjust this threshold as needed

    def on_press(self, key):
        if key == keyboard.Key.alt_l:
            self.pressed_keys.add('alt_l')
        elif key == keyboard.KeyCode.from_char('r'):
            self.pressed_keys.add('r')
            if 'alt_l' in self.pressed_keys and len(self.pressed_keys) == 2:
                if self.recording:
                    self.stop_recording()
                else:
                    self.start_recording()
        elif key == keyboard.Key.ctrl_l:
            self.pressed_keys.add('ctrl_l')
        elif key == keyboard.KeyCode.from_char('c'):
            if 'ctrl_l' in self.pressed_keys:
                print("Stopping the script...")
                self.stop_event.set()
                return False
        try:
            if self.recording:
                current_time = time.time() - self.start_time
                key_char = key.char
                if key_char not in self.pressed_keys and key_char != 'r':
                    if key_char in ['a', 'd', 's']:
                        event = None
                        if key_char == 'd':
                            event = "Fish moves to the left"
                        elif key_char == 'a':
                            event = "Fish moves to the right"
                        elif key_char == 's':
                            event = "Fish is being pulled towards the player"
                        self.annotations.append({"timestamp": current_time, "event": event, "action": f"press_{key_char}"})
                        self.pressed_keys.add(key_char)
                    elif key_char == 'o' and 'o' not in self.special_keys:
                        self.annotations.append({"timestamp": current_time, "event": "High Rod Tension", "action": "press_o"})
                        self.special_keys.add('o')
                    elif key_char == 't' and 't' not in self.special_keys:
                        self.annotations.append({"timestamp": current_time, "event": "Fishing Rod Breaks", "action": "press_t"})
                        self.special_keys.add('t')
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if self.recording:
                current_time = time.time() - self.start_time
                key_char = key.char
                if key_char in self.pressed_keys:
                    if key_char == 's':
                        self.annotations.append({"timestamp": current_time, "event": "Fishing Rod tension was too high", "action": "release_s"})
                    elif key_char not in ['p', 'r']:  # Exclude 'P' and 'R' (rod breaks button and record button) from release events
                        self.annotations.append({"timestamp": current_time, "action": f"release_{key_char}"})
                    self.pressed_keys.remove(key_char)
        except AttributeError:
            if key == keyboard.Key.alt_l:
                self.pressed_keys.remove('alt_l')
            elif key == keyboard.KeyCode.from_char('r'):
                self.pressed_keys.remove('r')
            elif key == keyboard.Key.ctrl_l:
                self.pressed_keys.remove('ctrl_l')

    def start_recording(self):
        if not self.recording:
            self.recording = True
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.temp_sequence_name = f"temp_fishing_sequence_{timestamp}"
            self.out = cv2.VideoWriter(os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4"), fourcc, 30.0, pyautogui.size())
            print("Recording started!")
            self.start_time = time.time()
            self.recording_thread = threading.Thread(target=self.record_frames)
            self.recording_thread.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.recording_thread.join()
            self.out.release()
            cv2.destroyAllWindows()

            sequence_name = input("Enter a name for the recorded sequence: ")
            os.rename(os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4"), os.path.join(self.output_dir, f"{sequence_name}.mp4"))

            with open(os.path.join(self.output_dir, f"{sequence_name}_annotations.json"), 'w') as f:
                json.dump(self.annotations, f, indent=2)

            print(f"Sequence '{sequence_name}' recorded and annotated successfully.")

    def record_frames(self):
        previous_tension_level = None
        
        while self.recording:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            rod_tension = self.estimate_rod_tension(frame, self.rod_roi)
            
            current_tension_level = None
            if rod_tension <= 30000:
                current_tension_level = "Low"
            elif rod_tension <= 60000:
                current_tension_level = "Mid"
            else:
                current_tension_level = "High"

            if current_tension_level != previous_tension_level:
                current_time = time.time() - self.start_time
                self.annotations.append({"timestamp": current_time, "event": "Rod Tension", "value": rod_tension, "level": current_tension_level})
                previous_tension_level = current_tension_level

            self.out.write(frame)
            cv2.imshow('Fishing Sequence', frame)
            cv2.waitKey(1)
            
    def estimate_rod_tension(self, frame, roi):
        # Extract the fishing rod ROI from the frame
        x, y, w, h = roi
        rod_roi = frame[y:y+h, x:x+w]

        # Convert the ROI to grayscale
        gray_roi = cv2.cvtColor(rod_roi, cv2.COLOR_BGR2GRAY)

        if self.prev_frame is None:
            self.prev_frame = gray_roi
            return 0

        # Calculate the absolute difference between the current and previous frames
        diff = cv2.absdiff(gray_roi, self.prev_frame)

        # Apply thresholding to the difference image
        _, thresh = cv2.threshold(diff, self.shake_threshold, 255, cv2.THRESH_BINARY)

        # Count the number of non-zero pixels in the thresholded image
        shake_intensity = cv2.countNonZero(thresh)

        # Update the previous frame
        self.prev_frame = gray_roi

        return shake_intensity

    def run(self):
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        try:
            self.stop_event.wait()
        except KeyboardInterrupt:
            print("Script interrupted by user.")
        finally:
            self.listener.stop()
            if self.recording:
                self.stop_recording()
            print("Script stopped.")

def main():
    output_dir = "fishing_sequences"
    os.makedirs(output_dir, exist_ok=True)

    print("Press 'Alt+R' to start/stop recording a fishing sequence.")
    print("Press 'Ctrl+C' to stop the script.")

    recorder = FishingSequenceRecorder(output_dir)
    recorder.run()

if __name__ == "__main__":
    main()