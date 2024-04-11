import cv2
import os
import time
import json
import numpy as np
from pynput import keyboard
from mss import mss

class FishingSequenceRecorder:
    def __init__(self, output_dir, sequence_name, duration):
        self.output_dir = output_dir
        self.sequence_name = sequence_name
        self.duration = duration
        self.out = None
        self.annotations = []
        self.start_time = 0
        self.listener = None
        self.sct = mss()
        self.pressed_keys = set()
        self.special_keys = set()

    def on_press(self, key):
        if key == keyboard.Key.esc:
            return False
        try:
            current_time = time.time() - self.start_time
            key_char = key.char
            if key_char not in self.pressed_keys:
                self.annotations.append({"timestamp": current_time, "action": f"press_{key_char}"})
                self.pressed_keys.add(key_char)
                
                # Annotate specific events
                if key_char == 'l':
                    self.annotations.append({"timestamp": current_time, "event": "Fish goes Left"})
                elif key_char == 'p':
                    self.annotations.append({"timestamp": current_time, "event": "Fish goes Right"})
                elif key_char == 'o' and 'o' not in self.special_keys:
                    self.annotations.append({"timestamp": current_time, "event": "Fishing Rod shakes over 50%"})
                    self.special_keys.add('o')
                elif key_char == 'k' and 'k' not in self.special_keys:
                    self.annotations.append({"timestamp": current_time, "event": "Fish got away"})
                    self.special_keys.add('k')
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            current_time = time.time() - self.start_time
            key_char = key.char
            if key_char in self.pressed_keys:
                if key_char not in ['o', 'k']:  # Exclude 'O' and 'K' from release events
                    self.annotations.append({"timestamp": current_time, "action": f"release_{key_char}"})
                self.pressed_keys.remove(key_char)
        except AttributeError:
            pass

    def record(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(os.path.join(self.output_dir, f"{self.sequence_name}.mp4"), fourcc, 30.0, (1920, 1080))

        self.start_time = time.time()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        while time.time() - self.start_time < self.duration:
            img = np.array(self.sct.grab(self.sct.monitors[1]))
            frame = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

            self.out.write(frame)

            cv2.imshow('Fishing Sequence', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to stop recording
                break

        self.out.release()
        cv2.destroyAllWindows()

        self.listener.stop()

        with open(os.path.join(self.output_dir, f"{self.sequence_name}_annotations.json"), 'w') as f:
            json.dump(self.annotations, f)

        print(f"Sequence '{self.sequence_name}' recorded and annotated successfully.")

def main():
    output_dir = "fishing_sequences"
    os.makedirs(output_dir, exist_ok=True)

    print("Press 'r' to start recording a fishing sequence.")
    print("Press 'Esc' to stop recording.")
    print("Press 'q' to quit.")

    while True:
        key = input("Enter your choice: ")
        if key == 'r':
            sequence_name = input("Enter the sequence name: ")
            duration = int(input("Enter the recording duration in seconds: "))
            recorder = FishingSequenceRecorder(output_dir, sequence_name, duration)
            recorder.record()
        elif key == 'q':
            break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()