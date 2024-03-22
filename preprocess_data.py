import numpy as np
from sklearn.model_selection import train_test_split

def preprocess_data(annotations):
    X = []
    y = []
    for annotation in annotations:
        fish_x, fish_y, rod_shake, key_input = annotation[1], annotation[2], annotation[3], annotation[4]
        # Normalize the values
        fish_x = fish_x / video_width
        fish_y = fish_y / video_height
        rod_shake = rod_shake / max_rod_shake
        # Encode the key input
        key_input_encoded = key_input_mapping[key_input]
        X.append([fish_x, fish_y, rod_shake])
        y.append(key_input_encoded)
    X = np.array(X)
    y = np.array(y)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_val, y_train, y_val