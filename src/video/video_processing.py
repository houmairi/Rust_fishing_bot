import cv2
import numpy as np

def detect_fish_movement(frame, previous_frame, threshold=30):
    # Convert frames to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate the absolute difference between the frames
    diff = cv2.absdiff(gray_frame, gray_previous_frame)
    
    # Threshold the difference image
    thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
    
    # Count the number of white pixels (movement)
    movement = cv2.countNonZero(thresh)
    
    # Determine the movement direction based on the position of white pixels
    left_movement = np.sum(thresh[:, :frame.shape[1]//2])
    right_movement = np.sum(thresh[:, frame.shape[1]//2:])
    
    if left_movement > right_movement:
        return "left"
    elif right_movement > left_movement:
        return "right"
    else:
        return "none"

def detect_rod_shake(frame, threshold=50):
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    
    # Detect edges using Canny edge detection
    edges = cv2.Canny(blurred_frame, 50, 150)
    
    # Count the number of edge pixels
    shake_intensity = cv2.countNonZero(edges)
    
    return shake_intensity

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video is opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        return
    
    # Get the video frame dimensions
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Initialize variables
    previous_frame = None
    fish_movement = "none"
    rod_shake_intensity = 0
    
    while True:
        # Read a frame from the video
        ret, frame = cap.read()
        
        # Break the loop if no more frames are available
        if not ret:
            break
        
        # Skip the first frame
        if previous_frame is None:
            previous_frame = frame
            continue
        
        # Detect fish movement
        fish_movement = detect_fish_movement(frame, previous_frame)
        
        # Detect rod shake intensity
        rod_shake_intensity = detect_rod_shake(frame)
        
        # Update the previous frame
        previous_frame = frame
        
        # Display the frame with annotations
        cv2.putText(frame, f"Fish Movement: {fish_movement}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Rod Shake Intensity: {rod_shake_intensity}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Fishing Analysis", frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the video capture and close windows
    cap.release()
    cv2.destroyAllWindows()

# Example usage
video_path = "data2process/test4.mp4"
process_video(video_path)