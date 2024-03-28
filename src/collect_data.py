import cv2
import os
import time

def record_fishing_sequence(output_dir, sequence_name, duration):
    cap = cv2.VideoCapture(0)  # Adjust the camera index if needed
    
    # Set the video codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(os.path.join(output_dir, f"{sequence_name}.mp4"), fourcc, 30.0, (640, 480))
    
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Write the frame to the output video file
        out.write(frame)
        
        cv2.imshow('Fishing Sequence', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def main():
    output_dir = "../../fishing_data/fishing_sequences"  # Modified relative path
    os.makedirs(output_dir, exist_ok=True)
    
    print("Press 'r' to start recording a fishing sequence.")
    print("Press 'q' to stop recording and quit.")
    
    while True:
        key = input("Enter your choice: ")
        if key == 'r':
            sequence_name = input("Enter the sequence name: ")
            duration = int(input("Enter the recording duration in seconds: "))
            record_fishing_sequence(output_dir, sequence_name, duration)
        elif key == 'q':
            break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()