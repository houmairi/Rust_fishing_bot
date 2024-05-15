import cv2
import numpy as np

# Set the desired contour area
contour_area = 1000

# Calculate the radius of the circle based on the contour area
radius = int(np.sqrt(contour_area / np.pi))

# Set the frame resolution
frame_width = 1280
frame_height = 720

# Create a blank frame
frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# Calculate the center coordinates of the circle
center_x = frame_width // 2
center_y = frame_height // 2

# Draw the circle on the frame
color = (0, 255, 0)  # Green color (BGR format)
thickness = -1  # Negative thickness means filled circle
cv2.circle(frame, (center_x, center_y), radius, color, thickness)

# Display the frame
cv2.imshow("Contour Area Visualization", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()