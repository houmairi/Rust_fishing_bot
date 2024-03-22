import numpy as np
from tensorflow.keras.models import load_model

def preprocess_input(fish_x, fish_y, rod_shake):
    # Normalize the input values
    fish_x = fish_x / video_width
    fish_y = fish_y / video_height
    rod_shake = rod_shake / max_rod_shake
    return np.array([[fish_x, fish_y, rod_shake]])

def predict_counter_movement(model, fish_x, fish_y, rod_shake):
    # Preprocess the input data
    input_data = preprocess_input(fish_x, fish_y, rod_shake)
    
    # Make predictions using the trained model
    predictions = model.predict(input_data)
    
    # Get the predicted counter-movement
    predicted_counter_movement = np.argmax(predictions)
    
    return predicted_counter_movement

# Load the trained model
model = load_model('models/fishing_model.h5')

# Example usage
fish_x = 100
fish_y = 200
rod_shake = 0.8

predicted_counter_movement = predict_counter_movement(model, fish_x, fish_y, rod_shake)
print("Predicted Counter-Movement:", predicted_counter_movement)