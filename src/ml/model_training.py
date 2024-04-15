import numpy as np
from src.ml.decision_tree import FishingDecisionTree

def train_model():
    # Load the preprocessed data from file
    data = np.load('preprocessed_data.npz')
    sequences = data['sequences']
    labels = data['labels']
    
    # Create and train the decision tree model
    model = FishingDecisionTree()
    model.train(sequences, labels)
    
    return model

if __name__ == '__main__':
    model = train_model()
    # Save the trained model to a file
    model.save('trained_model.pkl')