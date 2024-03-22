import cv2

def extract_frames(video_path, interval):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        cap.set(cv2.CAP_PROP_POS_MSEC, (cap.get(cv2.CAP_PROP_POS_MSEC) + interval))
    cap.release()
    return frames