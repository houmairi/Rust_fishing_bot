import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from src.ml.data_preprocessing import load_data, preprocess_data

def train_model(data_directory, test_size=0.2, random_state=42):
    # Load and preprocess the data
    sequences, labels = load_data(data_directory)
    X_train, X_test, y_train, y_test = preprocess_data(sequences, labels, test_size=test_size, random_state=random_state)

    # Create and train the Random Forest classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=random_state)
    clf.fit(X_train, y_train)

    # Evaluate the model on the testing set
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")

    return clf

def save_model(model, model_path):
    # Save the trained model to disk
    import joblib
    joblib.dump(model, model_path)