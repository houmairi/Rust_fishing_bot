#see what is being recognized ffsssssssssss, add a check if the thing recognized is roun
import cv2
import os
import time
import json
import numpy as np
from pynput import keyboard
import pyautogui
import threading

class FishingSequenceRecorder:
    def __init__(self, output_dir, bait_template_paths):
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
        self.bait_position = None
        self.recording_resolution = (1280, 720)  # Set the recording resolution to 1280x720
        self.bait_templates = [cv2.imread(path, 0) for path in bait_template_paths]  # Load the bait template images in grayscale
        self.bait_check_interval = 1  # Check bait position every 1 second
        self.last_bait_check_time = 0

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
            self.out = cv2.VideoWriter(os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4"), fourcc, 30.0, self.recording_resolution)
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

            sequence_name = input("Enter a name for the recorded sequence (or 'delete' to discard): ")
            
            if sequence_name.lower() == "delete":
                # Delete the temporary video file
                temp_video_path = os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4")
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                    print(f"Temporary video file '{self.temp_sequence_name}.mp4' deleted.")
                else:
                    print(f"Temporary video file '{self.temp_sequence_name}.mp4' not found.")
            else:
                # Rename the temporary video file
                os.rename(os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4"), os.path.join(self.output_dir, f"{sequence_name}.mp4"))

                # Save the annotations to a JSON file
                with open(os.path.join(self.output_dir, f"{sequence_name}_annotations.json"), 'w') as f:
                    json.dump(self.annotations, f, indent=2)

                print(f"Sequence '{sequence_name}' recorded and annotated successfully.")

    def record_frames(self):
        while self.recording:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Resize the frame to the desired recording resolution
            frame = cv2.resize(frame, self.recording_resolution)

            # Check bait position every second
            current_time = time.time()
            if current_time - self.last_bait_check_time >= self.bait_check_interval:
                self.last_bait_check_time = current_time

                # Detect the position of the bait (white and red ball)
                bait_position, bait_similarity, bait_image = self.detect_bait_position(frame)

                # Determine the relative position of the bait to the middle of the screen
                if bait_position is not None:
                    screen_width = frame.shape[1]
                    middle_x = screen_width // 2
                    bait_x = bait_position[0]

                    if bait_x < middle_x:
                        self.bait_position = "left"
                    elif bait_x > middle_x:
                        self.bait_position = "right"
                    else:
                        self.bait_position = "middle"

                    self.annotations.append({"timestamp": current_time - self.start_time, "event": f"Bait position: {self.bait_position}", "similarity": bait_similarity})

                    # Print the current bait position and similarity in the CLI
                    print(f"Current bait position: {self.bait_position}, Similarity: {bait_similarity:.2f}")

                    # Display the live picture of the detected bait
                    cv2.imshow("Detected Bait", bait_image)
                else:
                    # Print a message if the bait is not detected
                    print("Bait not detected")

            self.out.write(frame)
            cv2.imshow('Fishing Sequence', frame)
            cv2.waitKey(1)

    def detect_bait_position(self, frame):
        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        best_match = None
        best_match_val = 0
        best_match_template = None

        for template in self.bait_templates:
            # Perform template matching
            result = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_match_val:
                best_match = max_loc
                best_match_val = max_val
                best_match_template = template

        # Set a threshold for template matching confidence
        threshold = 0.6

        if best_match is not None and best_match_val >= threshold:
            # Get the coordinates of the top-left corner of the matched region
            bait_x, bait_y = best_match

            # Calculate the center coordinates of the bait
            bait_center_x = bait_x + best_match_template.shape[1] // 2
            bait_center_y = bait_y + best_match_template.shape[0] // 2

            # Extract the bait image from the frame
            bait_image = frame[bait_y:bait_y+best_match_template.shape[0], bait_x:bait_x+best_match_template.shape[1]]

            return (bait_center_x, bait_center_y), best_match_val, bait_image

        return None, 0, None

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

    bait_template_paths = ["fishing_bait.png", "fishing_bait2.png", "fishing_bait3.png"]  # Provide the paths to multiple bait template images

    print("Press 'Alt+R' to start/stop recording a fishing sequence.")
    print("Press 'Ctrl+C' to stop the script.")

    recorder = FishingSequenceRecorder(output_dir, bait_template_paths)
    recorder.run()

if __name__ == "__main__":
    main()