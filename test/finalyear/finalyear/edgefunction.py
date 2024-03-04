from flask import Flask, request, jsonify
import pickle
import pandas as pd
from pymongo import MongoClient
import numpy as np
from bson import ObjectId
from sklearn.linear_model import LinearRegression
import certifi
from sklearn.preprocessing import StandardScaler

ca = certifi.where()
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the pickled model
#with open(r'learnsync_server\test\Final year project\Final year project\random_forest_model.pkl', 'rb') as file:
    #loaded_model = pickle.load(file)
import ssl
import urllib
username = urllib.parse.quote_plus("shreyas")
password = urllib.parse.quote_plus("shreyas")

# Create a new client and connect to the server
client = MongoClient(
    "mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority" % (username, password),
    tlsAllowInvalidCertificates=True
)


db = client['learnsync']
users_collection = db['users']
question_collection=db['questions']
courses_collection = db['courses']
dataset_users=db['Dataset_users']

from flask import Flask, session, render_template

@app.route('/')
def index():
    # Set a value in the session
    session['user_ID'] = "65e2c5865f0817735e25d6b2"
    session['course_Name']='dsa'
    return "hello"



@app.route('/predict', methods=['GET'])
def predict():
    try:
        # Get the input data and user ID from the request
        # user_ID = session.get('user_ID', 'Guest')

        # opted = users_collection.find_one({'user_ID': user_ID})
        # opted_courses = opted.get('opted_courses')

        # user_performance = {}

        # def get_performance_details(user_id, c, course):
        #     for entry in course.get('performance', []):
        #         if entry.get('user_id') == user_id:
        #             user_performance[c] = {
        #                 'marks': entry.get('marks'),
        #                 'attempts': entry.get('attempts'),
        #                 'time spent': entry.get('time_spent')
        #             }
        #     return None  # Return None if user_id not found

        # for c in opted_courses:
        #     course = courses_collection.find_one({'course': c})
        #     get_performance_details(user_ID, c, course)
        #     user_performance[c]['course_ID'] = course.get('course_ID')

        # predictions = {}

        # Define custom weights for each feature
        weights = np.array([0.001, 0.4, 0.8, -0.02])

        # for i, j in user_performance.items():
        #     course_name = i
        #     course_id = j['course_ID']
        #     timespent = j['time spent']
        #     quizattempts = j['attempts']
        #     quizscore = j['marks']

        # Prepare input data for prediction
        input_data = {
            'course_id': 1,
            'timespent': 10,
            'quizscore': 10,
            'quizzattempts': 5
        }
        # Standardize the input data for prediction
        input_df = pd.DataFrame([input_data])
        input_features = np.array([input_data['timespent'], input_data['quizscore'], input_data['quizzattempts']]) * weights[1:]
        input_final = np.concatenate(([input_data['course_id']], input_features))
        user_id = ObjectId("65e2c5865f0817735e25d6b2")
        document = dataset_users.find_one({"user_id": user_id})
        if document:
            datasets_value = document.get("datasets")
            data = np.array([[float(entry['course_id']), float(entry['time_spent']),
                              float(entry['quiz_scores']), float(entry['quiz_attempts']),
                              float(entry['performance'])] for entry in datasets_value])
            X = data[:, :-1]
            y = data[:, -1]
            # Standardize the features
            # scaler = StandardScaler()
            # X_scaled = scaler.fit_transform(X)
            # Apply custom weights to the features (excluding 'course_id')
            X_weighted = X[:, 1:] * weights[1:]
            # Concatenate the weighted features with the non-weighted features (excluding 'course_id')
            X_final = np.concatenate((X[:, :1], X_weighted), axis=1)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_final)
            model = LinearRegression()
            model.fit(X_scaled, y)
            course = "dsa"
            # Predict using the loaded model
            weighted_features = np.array([input_data['timespent'], input_data['quizscore'], input_data['quizzattempts']]) * weights[1:]
            input_final = np.concatenate(([input_data['course_id']], weighted_features))
            input_final_scaled = scaler.transform(input_final.reshape(1, -1))
            prediction = model.predict(input_final_scaled)[0]
            # Ensure non-negative prediction
            user_id_to_update = session.get('user_ID', 'Guest')
            # Update the document in the MongoDB collection
            if prediction<=0.5:
                prediction=0
            elif prediction<=1.5:
                prediction=1
            else:
                prediction=2
            courses_collection.update_one(
                {'course': course, 'performance.user_id': user_id_to_update},
                {'$set': {'performance.$.performance': prediction}}
            )
            return {"success": "true", "performance": prediction}

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True,port=5008)