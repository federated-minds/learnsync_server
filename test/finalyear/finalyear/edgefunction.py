from flask import Flask, request, jsonify
import pickle
import pandas as pd
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the pickled model
with open(r'learnsync_server\test\Final year project\Final year project\random_forest_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

import urllib
username = urllib.parse.quote_plus("shreyas")
password = urllib.parse.quote_plus("shreyas")

# Create a new client and connect to the server
client = MongoClient("mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority"%(username,password))
db = client['learnsync']
users_collection = db['users']
question_collection=db['questions']
courses_collection = db['courses']

from flask import Flask, session, render_template

@app.route('/')
def index():
    # Set a value in the session
    session['user_ID'] = 9
    session['course_Name']='dsa'
    return "hello"


@app.route('/predict', methods=['GET'])
def predict():
    try:
        # Get the input data and user ID from the request
         
        user_ID = session.get('user_ID', 'Guest')
        print(user_ID)

        opted=users_collection.find_one({'user_ID':user_ID})
        opted_courses=opted.get('opted_courses')
        print(opted_courses)
        
       
    
        user_performance={}

        def get_performance_details(user_id,c,course):
            for entry in course.get('performance', []):
                if entry.get('user_id') == user_id:
                    user_performance[c] = {
                    'marks': entry.get('marks'),
                    'attempts': entry.get('attempts'),
                    'time spent':entry.get('time_spent')
                    }
                    print(user_performance)
            return None  # Return None if user_id not found

        # Example: Get details for user_id 5
        
        for c in opted_courses:
            print("C")
            course = courses_collection.find_one({'course': c})
            #print(user_performance[c])
            get_performance_details(user_ID,c,course)
            user_performance[c]['course_ID']=course.get('course_ID')      
            print('user_performance=',user_performance)
        
        # Get the student document from MongoDB
        #print(course)
        
        # Predict for each course
        predictions = {}
        for i,j in user_performance.items():
            course_name = i
            course_id=j['course_ID']
            timespent = j['time spent']
            quizattempts = j['attempts']
            quizscore = j['marks']
            
            # Prepare input data for prediction
            input_data = {
                'course_id': course_id,
                'timespent': timespent,
                'quizzattempts': quizattempts,
                'quizscore': quizscore
            }
            print(input_data)
            
            # Convert input data to DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Predict using the loaded model
            prediction = loaded_model.predict(input_df)[0]

            
            prediction=int(prediction)
            
            
            # Store prediction for the course in student document
            course_to_update = i
            user_id_to_update = user_ID
            new_performance_value = prediction  # Replace with the output from your model

            # Update the document in the MongoDB collection
            courses_collection.update_one(
                {'course': course_to_update, 'performance.user_id': user_id_to_update},
                {'$set': {'performance.$.performance': new_performance_value}}
            )
            
            # Store prediction value for the course
            
        
        return 'success'
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
