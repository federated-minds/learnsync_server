from flask import Flask, request, jsonify
import pickle
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)

# Load the pickled model
with open('random_forest_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
students_collection = db['students']

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data and user ID from the request
        data = request.json
        user_id = data.pop('__id__')  # Remove user_id from data
        
        # Get the student document from MongoDB
        student = students_collection.find_one({'__id__': user_id})
        if not student:
            return jsonify({'error': 'User not found'}), 404
        
        # Predict for each course
        predictions = {}
        for course in student.get('opted_courses', []):
            course_name = course.get('course_name')
            timespent = float(course.get('timespent', 0))
            quizattempts = int(course.get('quizzattempts', 0))
            quizscore = float(course.get('quizzscore', 0))
            
            # Prepare input data for prediction
            input_data = {
                'timespent': timespent,
                'quizzattempts': quizattempts,
                'quizscore': quizscore
            }
            
            # Convert input data to DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Predict using the loaded model
            prediction = loaded_model.predict(input_df)[0]
            
            # Store prediction for the course in student document
            students_collection.update_one(
                {'__id__': user_id, 'opted_courses.course_name': course_name},
                {'$set': {'opted_courses.$.predicted': prediction}}
            )
            
            # Store prediction value for the course
            predictions[course_name] = prediction
        
        return jsonify(predictions)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
