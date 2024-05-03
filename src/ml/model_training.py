import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

def train_model():
    # Load the preprocessed data from file
    data = np.load('preprocessed_data.npz', allow_pickle=True)
    sequences = data['sequences']
    labels = data['labels']
    
    # Encode the labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    
    # Convert sequences to numpy array
    sequences = np.array(sequences)
    
    # Reshape sequences if needed
    if len(sequences.shape) < 3:
        sequences = sequences.reshape(sequences.shape[0], -1)
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(sequences, encoded_labels, test_size=0.2, random_state=42)
    
    # Create and train the random forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")
    
    return model, label_encoder

if __name__ == '__main__':
    model, label_encoder = train_model()
    
    # Save the trained model and label encoder to files
    import joblib
    joblib.dump(model, 'trained_model.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')