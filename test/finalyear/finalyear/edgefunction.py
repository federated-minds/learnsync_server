from flask import Flask, request, jsonify
import pickle
import pandas as pd
from pymongo import MongoClient
import numpy as np
from bson import ObjectId
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the pickled model
#with open(r'learnsync_server\test\Final year project\Final year project\random_forest_model.pkl', 'rb') as file:
    #loaded_model = pickle.load(file)

import urllib
username = urllib.parse.quote_plus("shreyas")
password = urllib.parse.quote_plus("shreyas")

# Create a new client and connect to the server
client = MongoClient("mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority"%(username,password))
db = client['learnsync']
users_collection = db['users']
question_collection=db['questions']
courses_collection = db['courses']
dataset_users=db['Dataset_users']

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

        opted=users_collection.find_one({'user_ID':user_ID})
        opted_courses=opted.get('opted_courses')
        print(opted_courses)
        
       
    
        user_performance={}

        def get_performance_details(user_id,c,course):
            for entry in course.get('performance', []):
                print(entry)
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
            print(c)
            course = courses_collection.find_one({'course':c})
            #print(course)
            #print(user_performance[c])
            get_performance_details(user_ID,c,course)
            user_performance[c]['course_ID']=course.get('course_ID')      
            
        
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

            user_id = ObjectId("65e2c5865f0817735e25d6b2")
            document = dataset_users.find_one({"user_id": user_id})


            if document:
                datasets_value = document.get("datasets")
                print("Datasets for user_id {}: {}".format(user_id, datasets_value)) 
                data = np.array([[float(entry['course_id']),float(entry['time_spent']), float(entry['quiz_scores']),float(entry['quiz_attempts']), float(entry['performance'])] for entry in datasets_value])
                
                # Extract features and target variable
                X = data[:, :-1]  # Features
                y = data[:, -1]   # Target variable (performance)
                # Define custom weights for each feature
                weights = np.array([0.00001,0.01, 2, 1])  # Adjust these weights according to your preferences
                # Apply the custom weights to the features
                X_weighted = X[:, 1:] * weights[:-1]
                # Concatenate the weighted features with the non-weighted features (excluding 'course_id')
                X_final = np.concatenate((X[:, :1], X_weighted), axis=1)
                print(X_final,y)
            
                model = LinearRegression()
                model.fit(X_final,y)
            
            # Convert input data to DataFrame
                input_df = pd.DataFrame([input_data])
            
            # Predict using the loaded model
                prediction = model.predict(input_df)[0]
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