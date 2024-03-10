from flask import Flask, jsonify, request
from pymongo import MongoClient
import numpy as np
from scipy.stats import percentileofscore
import pickle
import pandas as pd
from bson import ObjectId
from sklearn.linear_model import LinearRegression
import certifi
from sklearn.preprocessing import StandardScaler
import ssl
import urllib

import dataset_rec

username = urllib.parse.quote_plus("shreyas")
password = urllib.parse.quote_plus("shreyas")
subject_recommendations = {
    
    "1": {
        "0": ["basic data types "],
        "1": ["dsa algorithms"],
        "2": ["Dynamic Programming"]
    },
    "2": {
        "0": ["sql basics"],
        "1": ["dbms","sql queries"],
        "2": ["normalisation in dbms"]
    },
    
    "3": {
        "0": ["python fundamentals"],
        "1": ["python oops"],
        "2": ["dsa in python","machine learning using python"]
    },
    "4": {
        "0": ["oops in c++"],
        "1": ["functions in c++"],
        "2": ["advanced c++ programming"]
    },
    "5": {
        "0": ["javascript basics"],
        "1": ["website using javascript"],
        "2": ["node js","express js"]
    },
    "6": {
        "0": ["basic physics", "basic maths"],
        "1": ["physics", "maths"],
        "2": ["advanced physics", "advanced maths"]
    },
    "7": {
        "0": ["Algebra"],
        "1": ["Probability"],
        "2": ["Integration","Advance Algebra"]
    },
    "8": {
        "0": ["parts of speech","basic grammar in english"],
        "1": ["essays"],
        "2": ["conversation proficiency in english"]
    },
    "9": {
        "0": ["oops in java"],
        "1": ["functions in java"],
        "2": ["advanced java programming"]
    },
    "10": {
        "0": ["vyavaharika kannada"],
        "1": ["kannada"],
        "2": ["aadalitha kannada"]
    },
}
# Load the pickled model
# with open(r'learnsync_server\test\Final year project\Final year project\random_forest_model.pkl', 'rb') as file:
#     loaded_model = pickle.load(file)

ca = certifi.where()
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create a new client and connect to the server
client = MongoClient(
    "mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority" % (username, password),
    tlsAllowInvalidCertificates=True
)

db = client['learnsync']
users_collection = db['users']
question_collection = db['questions']
courses_collection = db['courses']
dataset_users = db['Dataset_users']


@app.route('/aggregate_performance', methods=['POST'])
def aggregate_performance():
    input= request.json
    coursename = input["course_name"]
    course_id = input["course_id"]
    user_id = ObjectId(input["user_id"])
    performance_scores = {0: 0.2, 1: 0.5, 2: 0.8}
    print(input)

    # Retrieve all documents from the collection
    result = courses_collection.find_one({"course":coursename})
    # for entry in result:
    performance_data = result["performance"]

    student_marks = np.array([entry["score"] for entry in performance_data])
    local_predictions = np.array([performance_scores[entry["performance"]] for entry in performance_data])

    weights = student_marks / np.sum(student_marks)
    aggregated_prediction = np.sum(local_predictions * weights)
    print("Aggregated Prediction:", aggregated_prediction)

    if aggregated_prediction < 0.33:
        new_performance = "0"
    elif aggregated_prediction < 0.67:
        new_performance = "1"
    else:
        new_performance = "2"
    # Find the document with the specified user_id
    user_document = dataset_users.find_one({"user_id": user_id})
    print(new_performance)
    # Check if the user document is found
    if user_document:
        print("HI")
        # Update the performance value in the datasets array
        # for dataset in user_document['datasets']:
            # if dataset.get('course_id') == course_id:
        new_row = {
            "course_id": str(course_id),
            "time_spent": input["timespent"],
            "quiz_scores": input["quizscore"],
            "quiz_attempts": input["quizzattempts"],
            "performance": new_performance
        }
        print(new_row)
        result = dataset_users.update_one(
            {"user_id": user_id},
            {"$push": {"datasets": new_row}}
        )
        get_recommendations(input)
        return jsonify({"Success": "True, updated"})

    return jsonify({"error": "User not found or row not updated."})



# @app.route('/recommendations', methods=['GET'])
def get_recommendations(input):

    course_name = input["course_name"]
    course_id = input["course_id"]
    user_id = ObjectId(input["user_id"])
    course = courses_collection.find_one({'course': course_name})

    course_performance = course.get('performance', [])

    # extraction from Dataset_users
    def rec(course_id, user_id):
        user_document = dataset_users.find_one({"user_id": user_id})
        if user_document:
            # Access the datasets array within the document
            datasets = user_document.get("datasets", [])
            # Iterate through datasets to find the performance for the specified course_id
            for dataset in datasets[::-1]:
                if dataset.get("course_id") == str(course_id):
                    performance_value = dataset.get("performance")
                    print(f"Performance for course_id {course_id}: {performance_value}")
                    print(type(course_id))
                    print(type(performance_value))
                    return subject_recommendations[str(course_id)][str(performance_value)]
                else:
                    print(f"No dataset found for course_id {course_id} in user document.")
        else:
            print(f"No document found for user_id {user_id} in the dataset_users collection.")

    for user in course_performance:
        if user.get("user_id") == user_id:
            recommendations = rec(course_id, user_id)
            print(recommendations)
            # Update the document in the collection
            courses_collection.update_one(
                {"course": course_name, "performance.user_id": user_id},
                {"$set": {"performance.$[].recommendations": recommendations}}
            )

            return {"success": "Recommended successfully"}

  



if __name__ == '__main__':
    app.run(port=3001)
