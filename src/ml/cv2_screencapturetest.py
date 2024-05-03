import cv2

def select_roi(frame):
    # Display the frame
    cv2.imshow("Frame", frame)
    
    # Wait for the user to select the ROI
    roi = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
    
    # Destroy the window
    cv2.destroyAllWindows()
    
    return roi

def main():
    # Open the video file
    video_path = 'data2process/ez_catch1.mp4'
    cap = cv2.VideoCapture(video_path)
    
    # Read the first frame
    ret, frame = cap.read()
    
    if ret:
        # Select the ROI for the fishing rod
        roi = select_roi(frame)
        
        # Extract the ROI coordinates
        x, y, w, h = roi
        
        print("ROI Coordinates:")
        print(f"X: {x}, Y: {y}, Width: {w}, Height: {h}")
        
        # Iterate through the video frames
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Extract the fishing rod ROI from the frame
            rod_roi = frame[y:y+h, x:x+w]
            
            # Display the fishing rod ROI
            cv2.imshow("Fishing Rod ROI", rod_roi)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # Release the video capture and destroy windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()