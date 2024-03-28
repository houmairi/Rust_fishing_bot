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
    
    if shake_intensity >= threshold:
        return True
    else:
        return False