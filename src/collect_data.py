#hud off, graphics set to potato, water quality: 0, water reflections: 0

#{ AI SUGGESTION ON WHAT INFO COULD BE PROVIDED AS WELL TO MAKE BAIT DETECTION BETTER
#  "timestamp": 4.245351076126099,
#  "frame_number": 127,
#  "event": "Bait position",
#  "bounding_box": [600, 323, 680, 363],
#  "center_coordinates": [640, 343],
#  "confidence_score": 0.85,
#  "similarity": 0.6428571428571429,
#  "color_code": [157, 164, 208],
#  "context": {
#    "water_clarity": "clear",
#    "time_of_day": "daytime"
#  }
#}

#choosing a base where 2x2 water is being used as the environment.
import cv2
import os
import time
import json
import numpy as np
from pynput import keyboard
import pyautogui
import threading

class FishingSequenceRecorder:
    def __init__(self, output_dir, bait_threshold=100):
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
        #self.bait_templates = [cv2.imread(path, 0) for path in bait_template_paths]  # Load the bait template images in grayscale
        self.bait_check_interval = 1  # Check bait position every 1 second
        self.last_bait_check_time = 0
        self.bait_threshold = bait_threshold

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
        cv2.namedWindow("Fishing Sequence")
        cv2.namedWindow("Detected Bait")

        while self.recording:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Resize the frame to the desired recording resolution
            frame = cv2.resize(frame, self.recording_resolution)

            # Get the frame dimensions
            height, width, _ = frame.shape

            # Define the middle field coordinates
            middle_start = int(width * 0.4)  # Adjust the factor as needed
            middle_end = int(width * 0.6)  # Adjust the factor as needed

            # Draw lines to visualize the middle field
            cv2.line(frame, (middle_start, 0), (middle_start, height), (255, 0, 0), 2)
            cv2.line(frame, (middle_end, 0), (middle_end, height), (255, 0, 0), 2)

            # Display the coordinates at the top-left and bottom-right corners
            cv2.putText(frame, "(0, 0)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"({width}, {height})", (width - 150, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Check bait position every second
            current_time = time.time()
            if current_time - self.last_bait_check_time >= self.bait_check_interval:
                self.last_bait_check_time = current_time

                # Detect the position of the bait (red color)
                bait_position, bait_similarity, bait_image, color_code = self.detect_bait_position(frame)

                # Determine the relative position of the bait to the middle field
                if bait_position is not None:
                    bait_x, bait_y = bait_position

                    if middle_start <= bait_x <= middle_end:
                        self.bait_position = "middle"
                    elif bait_x < middle_start:
                        self.bait_position = "left"
                    else:
                        self.bait_position = "right"

                    self.annotations.append({
                        "timestamp": current_time - self.start_time,
                        "event": f"Bait position: {self.bait_position} (x={bait_x}, y={bait_y})",
                        "similarity": bait_similarity,
                        "color_code": color_code
                    })

                    # Print the current bait position, coordinates, similarity, and color code in the CLI
                    print(f"Current bait position: {self.bait_position} (x={bait_x}, y={bait_y}), Similarity: {bait_similarity:.2f}, Color Code: {color_code}")

                    # Draw a circle around the recognized bait position
                    cv2.circle(frame, (bait_x, bait_y), 20, (0, 255, 0), 2)

                    # Display the live picture of the detected bait
                    cv2.imshow("Detected Bait", bait_image)
                else:
                    # Print a message if the bait is not detected
                    print("Bait not detected")
                    cv2.imshow("Detected Bait", np.zeros((100, 100, 3), dtype=np.uint8))

            self.out.write(frame)
            cv2.imshow("Fishing Sequence", frame)
            cv2.waitKey(1)

        cv2.destroyAllWindows()

    def detect_bait_position(self, frame):
        # Define the color range for the red color
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        # Create a mask for the red color range
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        red_mask1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        # Find contours of the red regions
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on aspect ratio and size
        min_aspect_ratio = 1
        max_aspect_ratio = 2
        min_contour_area = 25   # Adjust based on the smallest expected half-circle bait size
        max_contour_area = 1000  # Adjust based on the largest expected half-circle bait size

        filtered_contours = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            contour_area = cv2.contourArea(contour)

            if min_aspect_ratio <= aspect_ratio <= max_aspect_ratio and min_contour_area <= contour_area <= max_contour_area:
                filtered_contours.append(contour)

        if len(filtered_contours) > 0:
            # Find the contour with the largest area (assumed to be the bait)
            largest_contour = max(filtered_contours, key=cv2.contourArea)

            # Calculate the center coordinates of the bait
            moments = cv2.moments(largest_contour)
            if moments["m00"] != 0:
                bait_center_x = int(moments["m10"] / moments["m00"])
                bait_center_y = int(moments["m01"] / moments["m00"])

                # Extract the bait image from the frame
                x, y, w, h = cv2.boundingRect(largest_contour)
                bait_image = frame[y:y+h, x:x+w]

                # Get the average color of the bait image
                avg_color = np.mean(bait_image, axis=(0, 1)).astype(int)
                color_code = (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

                # Check if the average color falls within the expected range for red
                if color_code[2] < 180:  # Adjust this threshold as needed
                    return (bait_center_x, bait_center_y), cv2.contourArea(largest_contour) / self.bait_threshold, bait_image, color_code

        return None, 0, None, None

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

    #bait_template_paths = ["fishing_bait.png", "fishing_bait2.png", "fishing_bait3.png"]  # Provide the paths to multiple bait template images

    print("Press 'Alt+R' to start/stop recording a fishing sequence.")
    print("Press 'Ctrl+C' to stop the script.")
    
    bait_threshold = 70  # Adjust the threshold value as needed
    recorder = FishingSequenceRecorder(output_dir, bait_threshold)
    recorder.run()

if __name__ == "__main__":
    main()