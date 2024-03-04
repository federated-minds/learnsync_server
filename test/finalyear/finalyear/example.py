import numpy as np

def aggregate_performance(local_predictions, student_marks):
    # Define mapping from local predictions to performance scores
    performance_scores = {0: 0.2, 1: 0.5, 2: 0.8}
    
    # Calculate weights based on student marks (higher marks, higher weight)
    weights = student_marks / np.sum(student_marks)
    
    # Aggregate local predictions using weighted average
    aggregated_prediction = np.sum(np.array([performance_scores[pred] for pred in local_predictions]) * weights)
    
    # Define performance categories
    if aggregated_prediction < 0.33:
        new_performance = "Poor"
    elif aggregated_prediction < 0.67:
        new_performance = "Fair"
    else:
        new_performance = "Good"
    
    return new_performance, aggregated_prediction

# Example data (local predictions and student marks)
local_predictions = np.array([2, 1, 2])  # Sample local predictions (0 for poor, 1 for fair, 2 for good)
student_marks = np.array([80, 65, 60])   # Sample student marks

# Calculate aggregated performance
new_performance, aggregated_prediction = aggregate_performance(local_predictions, student_marks)

print("Aggregated Performance:", new_performance)
print("Aggregated Prediction:", aggregated_prediction)