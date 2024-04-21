import cv2
import numpy as np
import os

class FishCaughtDetector:
    def __init__(self, reference_images_path):
        self.reference_images_path = reference_images_path
        self.reference_images = self._load_reference_images()

    def _load_reference_images(self):
        reference_images = {}
        for filename in os.listdir(self.reference_images_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image_path = os.path.join(self.reference_images_path, filename)
                image = cv2.imread(image_path)
                fish_name = os.path.splitext(filename)[0]
                reference_images[fish_name] = image
        return reference_images

    def is_fish_caught(self, screen_image):
        for fish_name, reference_image in self.reference_images.items():
            result = cv2.matchTemplate(screen_image, reference_image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= 0.8:  # Adjust the threshold as needed
                return fish_name
        return None

    def preprocess_image(self, image):
        # Crop the region of interest (bottom right corner)
        roi = image[image.shape[0]-100:, image.shape[1]-300:]
        
        # Resize the cropped image to match the reference image size
        resized_roi = cv2.resize(roi, (self.reference_images[0].shape[1], self.reference_images[0].shape[0]))
        
        return resized_roi

    def compare_images(self, image1, image2):
        # Convert the images to grayscale
        gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the images
        diff = cv2.absdiff(gray_image1, gray_image2)

        # Threshold the difference image
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # Count the number of non-zero pixels in the thresholded image
        non_zero_pixels = cv2.countNonZero(thresh)

        # Calculate the similarity percentage
        total_pixels = gray_image1.shape[0] * gray_image1.shape[1]
        similarity = 1 - (non_zero_pixels / total_pixels)

        # Check if the similarity is above a certain threshold
        if similarity >= 0.9:
            return True
        else:
            return False