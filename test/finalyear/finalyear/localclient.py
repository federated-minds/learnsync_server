import pickle
import pandas as pd
import json
# Load the pickled model file
with open('random_forest_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

df = pd.read_csv("mock2.csv")
result = {}

for index, course in df.iterrows():
    # Create a DataFrame from the row
    input_data = pd.DataFrame([{
        "course_id": course["course_id"],
        "time_spent": course["time_spent"],
        "quiz_scores": course["quiz_scores"],
        "quiz_attempts": course["quiz_attempts"]
    }])
    
    # Ensure the input data has the correct data types
    input_data = input_data.astype({"course_id": int, "time_spent": float, "quiz_scores": float, "quiz_attempts": int})
    
    # Predict using the loaded model
    res = loaded_model.predict(input_data)
    
    result[course["course_id"]] = res[0]  # Assuming res is an array with a single prediction value
output=json.dumps(result)
print(output)
