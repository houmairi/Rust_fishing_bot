import os
import sys
import cv2
import json
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

def preprocess_data(data_directory, iteration_directory):
    metadata = []

    for filename in os.listdir(data_directory):
        if filename.endswith(".mp4"):
            video_path = os.path.join(data_directory, filename)
            annotation_path = os.path.join(data_directory, f"{os.path.splitext(filename)[0]}_annotations.json")

            if not os.path.exists(annotation_path):
                print(f"Annotation file not found for video: {filename}")
                continue

            with open(annotation_path, 'r') as f:
                video_annotations = json.load(f)

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Error opening video file: {video_path}")
                continue

            for annotation in video_annotations:
                timestamp = annotation['timestamp']
                event = annotation.get('event', '')
                action = annotation.get('action', '')

                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
                ret, frame = cap.read()

                if ret:
                    frame_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.jpg"
                    frame_path = os.path.join(iteration_directory, frame_filename)
                    cv2.imwrite(frame_path, frame)
                    
                    label = f"{event}_{action}" if event else action
                    metadata.append({"file_path": frame_path, "label": label, "timestamp": timestamp})

            cap.release()

    metadata_path = os.path.join(iteration_directory, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Preprocessing completed. Frames and metadata saved to '{iteration_directory}'.")

if __name__ == '__main__':
    data_directory = 'C:/Users/Niko/Documents/Repositorys/rust-fishing-bot/src/ml/data2process'
    
    # Create a new directory for each iteration
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    iteration_directory = os.path.join(data_directory, f"iteration_{timestamp}")
    os.makedirs(iteration_directory, exist_ok=True)
    
    preprocess_data(data_directory, iteration_directory)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# Fishing rod tension estimation functions (commented out)
#ROI Coordinates of fishing rod: X: 1199, Y: 266, Width: 754, Height: 1141
# def preprocess_frame(frame):
#     # Resize the frame to a fixed size
#     resized_frame = cv2.resize(frame, (640, 480))
    
#     # Convert the frame to grayscale
#     gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    
#     # Apply Gaussian blur to reduce noise
#     blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    
#     return blurred_frame

# def extract_rod_contour(frame):
#     # Apply edge detection
#     edges = cv2.Canny(frame, 50, 150)
    
#     # Find contours in the edge map
#     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     # Find the contour with the largest area (assumed to be the fishing rod)
#     rod_contour = max(contours, key=cv2.contourArea)
    
#     return rod_contour

# def estimate_tension(rod_contour):
#     # Calculate the bounding rectangle of the rod contour
#     x, y, w, h = cv2.boundingRect(rod_contour)
    
#     # Calculate the aspect ratio of the bounding rectangle
#     aspect_ratio = float(w) / h
    
#     # Estimate the tension based on the aspect ratio
#     if aspect_ratio > 1.5:
#         tension = 0.2
#     elif 1.2 <= aspect_ratio <= 1.5:
#         tension = 0.5
#     else:
#         tension = 0.8
    
#     return tension

# def estimate_rod_tension(frame, roi):
#     # Extract the fishing rod ROI from the frame
#     x, y, w, h = roi
#     rod_roi = frame[y:y+h, x:x+w]
    
#     # Preprocess the rod ROI
#     preprocessed_roi = preprocess_frame(rod_roi)
    
#     try:
#         # Extract the fishing rod contour from the ROI
#         rod_contour = extract_rod_contour(preprocessed_roi)
        
#         # Estimate the tension based on the rod contour
#         tension = estimate_tension(rod_contour)
        
#         return tension
    
#     except ValueError:
#         # Handle cases where no contour is found
#         return 0.0