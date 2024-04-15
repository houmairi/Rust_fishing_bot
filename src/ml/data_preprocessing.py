import os
import sys
import cv2

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from ..video.video_processing import detect_fish_movement, detect_rod_shake

def preprocess_data(data_directory):
    sequences = []
    labels = []
    
    for filename in os.listdir(data_directory):
        if filename.endswith(".mp4"):
            filepath = os.path.join(data_directory, filename)
            frames = []
            
            # Read the video file
            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                print(f"Error opening video file: {filepath}")
                continue
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            cap.release()
            
            # Process the frames to extract features
            previous_frame = frames[0]
            for frame in frames[1:]:
                fish_movement = detect_fish_movement(frame, previous_frame)
                rod_shake = detect_rod_shake(frame)
                
                # Create feature vector
                feature_vector = [fish_movement, rod_shake]
                sequences.append(feature_vector)
                
                # Create label based on the decision tree
                if fish_movement == "left":
                    if rod_shake < 50:
                        label = "hold_d"
                    else:
                        label = "release_d"
                elif fish_movement == "right":
                    if rod_shake < 50:
                        label = "hold_a"
                    else:
                        label = "release_a"
                else:
                    if rod_shake < 50:
                        label = "hold_s"
                    else:
                        label = "release_s"
                
                labels.append(label)
                previous_frame = frame
    
    return sequences, labels

if __name__ == '__main__':
    data_directory = '/data2process'
    sequences, labels = preprocess_data(data_directory)
    print("Preprocessing completed.")