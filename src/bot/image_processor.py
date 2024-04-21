import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        pass

    def preprocess_image(self, image):
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to create a binary image
        _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Perform additional preprocessing steps if needed
        # ...
        
        return thresh_image