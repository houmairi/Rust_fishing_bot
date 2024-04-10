import cv2
import os
import time
import json
import numpy as np
from pynput import keyboard

class FishingSequenceRecorder:
    def __init__(self, output_dir, sequence_name, duration):
        self.output_dir = output_dir
        self.sequence_name = sequence_name
        self.duration = duration
        self.cap = None
        self.out = None
        self.annotations = []
        self.start_time = 0
        self.listener = None

    def on_press(self, key):
        if key == keyboard.Key.esc:
            return False
        try:
            current_time = time.time() - self.start_time
            self.annotations.append({"timestamp": current_time, "action": key.char})
        except AttributeError:
            pass

    def record(self):
        self.cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(os.path.join(self.output_dir, f"{self.sequence_name}.mp4"), fourcc, 30.0, (640, 480))

        self.start_time = time.time()
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        while time.time() - self.start_time < self.duration:
            ret, frame = self.cap.read()
            if not ret:
                break

            self.out.write(frame)

            cv2.imshow('Fishing Sequence', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to stop recording
                break

        self.cap.release()
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