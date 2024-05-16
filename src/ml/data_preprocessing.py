import os
import sys
import cv2
import json
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

def preprocess_data(high_directory, low_directory, iteration_directory):
    metadata = []

    for tension_state, data_directory in [("high", high_directory), ("low", low_directory)]:
        for filename in os.listdir(data_directory):
            if filename.endswith(".mp4"):
                video_path = os.path.join(data_directory, filename)

                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print(f"Error opening video file: {video_path}")
                    continue

                frame_count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame_filename = f"{tension_state}_{os.path.splitext(filename)[0]}_{frame_count}.jpg"
                    frame_path = os.path.join(iteration_directory, frame_filename)
                    cv2.imwrite(frame_path, frame)

                    metadata.append({"file_path": frame_path, "label": tension_state})
                    frame_count += 1

                cap.release()

    metadata_path = os.path.join(iteration_directory, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Preprocessing completed. Frames and metadata saved to '{iteration_directory}'.")

if __name__ == '__main__':
    high_directory = 'C:/Users/Niko/Documents/Repositorys/rust-fishing-bot/src/ml/labeled_data/trainingdata/high'
    low_directory = 'C:/Users/Niko/Documents/Repositorys/rust-fishing-bot/src/ml/labeled_data/trainingdata/low'
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    iteration_directory = os.path.join(os.path.dirname(high_directory), f"iteration_{timestamp}")
    os.makedirs(iteration_directory, exist_ok=True)
    
    preprocess_data(high_directory, low_directory, iteration_directory)