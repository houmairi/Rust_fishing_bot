import cv2
import numpy as np
import os
import pytesseract

class FishCaughtDetector:
    def __init__(self):
        pass

    def is_fish_caught(self, screen_image):
        # Preprocess the screen image
        preprocessed_image = self.preprocess_image(screen_image)

        # Extract the text from the preprocessed image
        extracted_text = self.extract_text_from_image(preprocessed_image)

        # Compare the extracted text with the list of fish names
        caught_fish = self.compare_text_with_fish_names(extracted_text)

        return caught_fish

    def preprocess_image(self, image):
        # Convert the image to the HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the range of green color in HSV
        #lower_green = np.array([60, 10, 20])
        #upper_green = np.array([130, 50, 40])

        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])

        # Create a mask for green color
        mask = cv2.inRange(hsv_image, lower_green, upper_green)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour (pop-up)
        largest_contour = max(contours, key=cv2.contourArea)

        # Draw a bounding rectangle around the contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Extract the region of interest (ROI) from the original image
        roi = image[y:y+h, x:x+w]

        return roi

    def extract_text_from_image(self, image):
        try:
            # Specify the path to the Tesseract executable
            tesseract_path = r'C:\Users\Niko\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
            
            # Apply OCR using Tesseract
            text = pytesseract.image_to_string(image)
            #print(text)
            return text
        except pytesseract.TesseractError as e:
            print(f"Tesseract OCR error: {str(e)}")
            return ""

    def compare_text_with_fish_names(self, text):
        # List of possible fish names
        fish_names = ["anchovy", "herring", "human skull", "orange roughy", "salmon", "sardine", "small shark", "small trout", "small waterbottle", "tarp", "diving fins", "water jug", "catfish", "yellow perch", "water bucket"] #safe zone exception einbauen

        # Remove any whitespace and convert to lowercase
        text = text.strip().lower()

        # Check if the extracted text matches any fish name
        for fish_name in fish_names:
            if fish_name in text:
                return fish_name

        return None