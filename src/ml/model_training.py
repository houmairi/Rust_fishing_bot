from src.ml.data_preprocessing import preprocess_data
from src.ml.decision_tree import FishingDecisionTree

def train_model(data_directory):
    # Preprocess the data
    sequences, labels = preprocess_data(data_directory)
    
    # Create and train the decision tree model
    model = FishingDecisionTree()
    model.train(sequences, labels)
    
    return model