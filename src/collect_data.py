import cv2
import os
import time
import json
import numpy as np
from pynput import keyboard
import pyautogui

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

    def on_press(self, key):
        if key == keyboard.Key.ctrl_l:
            self.pressed_keys.add('ctrl_l')
        elif key == keyboard.KeyCode.from_char('f'):
            if 'ctrl_l' in self.pressed_keys:
                self.stop_recording()
                return False
        elif key == keyboard.Key.alt_l:
            self.pressed_keys.add('alt_l')
        elif key == keyboard.KeyCode.from_char('r'):
            if 'alt_l' in self.pressed_keys:
                self.start_recording()
        try:
            if self.recording:
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
            if self.recording:
                current_time = time.time() - self.start_time
                key_char = key.char
                if key_char in self.pressed_keys:
                    if key_char not in ['o', 'k']:  # Exclude 'O' and 'K' from release events
                        self.annotations.append({"timestamp": current_time, "action": f"release_{key_char}"})
                    self.pressed_keys.remove(key_char)
        except AttributeError:
            if key == keyboard.Key.ctrl_l:
                self.pressed_keys.remove('ctrl_l')
            elif key == keyboard.Key.alt_l:
                self.pressed_keys.remove('alt_l')

    def start_recording(self):
        if not self.recording:
            self.recording = True
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.temp_sequence_name = f"temp_fishing_sequence_{timestamp}"
            self.out = cv2.VideoWriter(os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4"), fourcc, 30.0, pyautogui.size())
            print("Recording started!")
            self.start_time = time.time()
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            self.record_frames()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.out.release()
            cv2.destroyAllWindows()
            self.listener.stop()
            
            sequence_name = input("Enter a name for the recorded sequence: ")
            os.rename(os.path.join(self.output_dir, f"{self.temp_sequence_name}.mp4"), os.path.join(self.output_dir, f"{sequence_name}.mp4"))
            
            with open(os.path.join(self.output_dir, f"{sequence_name}_annotations.json"), 'w') as f:
                json.dump(self.annotations, f)
            
            print(f"Sequence '{sequence_name}' recorded and annotated successfully.")

    def record_frames(self):
        while self.recording:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            self.out.write(frame)
            cv2.imshow('Fishing Sequence', frame)
            cv2.waitKey(1)

def main():
    output_dir = "fishing_sequences"
    os.makedirs(output_dir, exist_ok=True)

    print("Press 'Alt+R' to start recording a fishing sequence.")
    print("Press 'Ctrl+F' to stop recording.")

    recorder = FishingSequenceRecorder(output_dir)

    with keyboard.Listener(on_press=recorder.on_press, on_release=recorder.on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()