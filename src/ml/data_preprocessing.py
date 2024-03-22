import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_data(data_directory):
    # Load the fishing sequences and labels from the data directory
    sequences = []
    labels = []

    for filename in os.listdir(data_directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(data_directory, filename)
            data = pd.read_csv(filepath)
            sequences.append(data[["fish_movement", "rod_shake"]].values)
            labels.append(data["counter_movement"].values)

    sequences = np.concatenate(sequences, axis=0)
    labels = np.concatenate(labels, axis=0)

    return sequences, labels

def preprocess_data(sequences, labels, test_size=0.2, random_state=42):
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(sequences, labels, test_size=test_size, random_state=random_state)

    # Scale the features using StandardScaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test