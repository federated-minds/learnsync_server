from flask import Flask, request, jsonify
import pickle
import pandas as pd
from pymongo import MongoClient
import numpy as np
from bson import ObjectId
from sklearn.linear_model import LinearRegression
import certifi
from sklearn.preprocessing import StandardScaler
import requests
import json
import utils 
import tenseal as ts
from bson.binary import Binary
from gridfs import GridFS

##  INitializor for encryptions
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
context.global_scale = 2**40
secret_context = context.serialize(save_secret_key=True)
utils.write_data("K:/Final Year Project/code/learnsync_server/test/finalyear/finalyear/keys/secret.txt", secret_context)
context.make_context_public()
public_context = context.serialize()
utils.write_data("K:/Final Year Project/code/learnsync_server/test/finalyear/finalyear/keys/public.txt", public_context)

ca = certifi.where()
app = Flask(__name__)
# app.secret_key = 'your_secret_key'

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


def encrypt(prediction,uid):
    vec =[prediction]
    context = ts.context_from(utils.read_data("K:/Final Year Project/code/learnsync_server/test/finalyear/finalyear/keys/public.txt"))
    encry_pred = ts.ckks_vector(context, vec)
    utils.write_data("K:/Final Year Project/code/learnsync_server/comms/encrypted_prediction.txt", encry_pred.serialize()) 
    fs = GridFS(db)
    with open("K:/Final Year Project/code/learnsync_server/comms/encrypted_prediction.txt", 'rb') as file:
        file_id = fs.put(file, filename=f'encrypted_prediction_{uid}.txt')
    print("file uploaded",file_id)

    

@app.route('/predict', methods=['POST'])
def predict():

    eval_data = request.json

    weights = np.array([0.001, 0.4, 0.8, -0.02])
    input_data=eval_data
    print(input_data)
    # Standardize the input data for prediction
    input_df = pd.DataFrame([input_data])
    input_features = np.array([input_data['timespent'], input_data['quizscore'], input_data['quizzattempts']]) * weights[1:]
    input_final = np.concatenate(([input_data['course_id']], input_features))
    user_id = ObjectId(input_data["user_id"])
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
        print("hii")
        # print(input_data)
        course = input_data["course_name"]
        # print(course)
        # Predict using the loaded model
        weighted_features = np.array([input_data['timespent'], input_data['quizscore'], input_data['quizzattempts']]) * weights[1:]
        input_final = np.concatenate(([input_data['course_id']], weighted_features))
        input_final_scaled = scaler.transform(input_final.reshape(1, -1))
        prediction = model.predict(input_final_scaled)[0]
        print("model pred",prediction)
        # Ensure non-negative prediction
        user_id_to_update = ObjectId(input_data['user_id'])
        # print(user_id_to_update)
        # print(type(user_id_to_update))
        # Update the document in the MongoDB collection
        if prediction<=0.5:
            prediction=0
        elif prediction<=1.5:
            prediction=1
        else:
            prediction=2
        print(prediction)
        encrypt(prediction,user_id_to_update)
        
        # print(courses_collection.find_one({'course': course, 'performance.user_id': user_id_to_update}))
        courses_collection.update_many(
            {'course': course, 'performance.user_id': user_id_to_update},
            {'$set': {'performance.$[].performance': prediction}},
                        
        )
        url = 'http://localhost:3001/aggregate_performance'
        response = requests.post(url, json=input_data)


        return {"success": "true", "performance": prediction}


if __name__ == '__main__':
    app.run(port=3000)