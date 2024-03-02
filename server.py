from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import certifi
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from bson import ObjectId
ca = certifi.where()
app = Flask(__name__)
CORS(app)  

# Connect to MongoDB
import urllib
username = urllib.parse.quote_plus("sandeep")
password = urllib.parse.quote_plus("sandeep")



# Create a new client and connect to the server
client = MongoClient("mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority" % (username, password),
                      tlsCAFile=ca)
db = client['learnsync']
users_collection = db['users']
question_collection=db['questions']
courses_collection = db['courses']
dataset_users=db['Dataset_users']



try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        hashed_password = generate_password_hash(data['password'])
        user = {
            'name': data['name'],
            'email': data['email'],
            'password': data['password']# Use the hashed password for security
        }
        result = users_collection.insert_one(user)

        # Insert an empty document with the user's ID into another collection
        other_document = {'user_id': result.inserted_id, 'datasets': [{'course_id': '1', 'time_spent': '55', 'quiz_scores': '19', 'quiz_attempts': '5', 'performance': '0'},
{'course_id': '1', 'time_spent': '8', 'quiz_scores': '6', 'quiz_attempts': '4', 'performance': '0'},
{'course_id': '10', 'time_spent': '51', 'quiz_scores': '100', 'quiz_attempts': '2', 'performance': '2'},
{'course_id': '2', 'time_spent': '6', 'quiz_scores': '54', 'quiz_attempts': '1', 'performance': '1'},
{'course_id': '2', 'time_spent': '51', 'quiz_scores': '63', 'quiz_attempts': '2', 'performance': '1'}]}
        dataset_users.insert_one(other_document)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        print(data)
        user = users_collection.find_one({'email': data['email']})
        if user and (user['password']==data['password']):
            #session.setItem('user_ID', user);
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
    
tests = [
    {"name": "maths", "time": "10:00 AM", "date": "2024-02-16"},
    {"name": "BTC", "time": "11:30 AM", "date": "2024-02-17"},
    {"name": "AML", "time": "02:00 PM", "date": "2024-02-18"},
]
@app.route("/tests")
def get_tests():
    return jsonify(tests)



@app.route("/questions")
def get_questions():
    test_name = request.args.get("test_name")
    if not test_name:
        return jsonify({"error": "Test name is required"}), 400

    # Query MongoDB for questions data based on the test name
    questions_data = list(question_collection.find({"subname": test_name}).limit(5))

    # Extract only the question strings from the documents
    questions = [question["question"] for question in questions_data]

    return jsonify(questions)


@app.route('/submit-answers', methods=['POST'])
def submit_answers():
    res = request.get_json()
    submitted_answers = res['answers']
    subject_name = res['testName']

    # Query MongoDB for the correct answers based on the subject name
    correct_answers_data = list(question_collection.find({"subname": subject_name}).limit(len(submitted_answers)))
    correct_answers = [question["answer"] for question in correct_answers_data]
    print(correct_answers)

    # Evaluate the score
    score = sum(1 for submitted, correct in zip(submitted_answers, correct_answers) if submitted == correct)

    print("Received answers:")
    for index, answer in enumerate(submitted_answers):
        print(f"Question {index + 1}: {answer}")

    print(f"Score: {score} / {len(correct_answers)}")
    course_id=1
    time_spent=8
    quiz_scores=score
    quiz_attempts=4
    performance=-1
    user_id = ObjectId("65e2c5865f0817735e25d6b2")
    document = dataset_users.find_one({"user_id": user_id})
    if document:
        datasets_value = document.get("datasets")
        print("Datasets for user_id {}: {}".format(user_id, datasets_value)) 
        data = np.array([    [float(entry['course_id']), float(entry['time_spent']), float(entry['quiz_scores']),float(entry['quiz_attempts']), float(entry['performance'])] for entry in datasets_value])
        # Extract features and target variable
        X = data[:, :-1]  # Features
        y = data[:, -1]   # Target variable (performance)
        # Define custom weights for each feature
        weights = np.array([0.2, 0.3, 0.5, 0.4])  # Adjust these weights according to your preferences
        # Apply the custom weights to the features
        X_weighted = X[:, 1:] * weights[:-1]
        # Concatenate the weighted features with the non-weighted features (excluding 'course_id')
        X_final = np.concatenate((X[:, :1], X_weighted), axis=1)
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42)
        # Train a linear regression model
        model = LinearRegression()
        model.fit(X_train, y_train)
        # Make predictions on the test set
        y_pred = model.predict(X_test)
        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error: {mse}')
        # Get the coefficients (weights) learned by the model
        coefficients = model.coef_
        print(f'Coefficients (weights): {coefficients}')
        new_data = np.array([[course_id, time_spent, quiz_scores, quiz_attempts]])
        # Define custom weights for each feature
        weights = np.array([0.2, 0.3, 0.7, 0.4])  # Adjust these weights according to your preferences
        # Apply the custom weights to the features
        new_data_weighted = new_data[:, 1:] * weights[1:]
        # Concatenate the weighted features with the non-weighted features (excluding 'course_id')
        new_data_final = np.concatenate((new_data[:, :1], new_data_weighted), axis=1)
        # Predict performance for the new data using the earlier trained model
        predicted_performance = model.predict(new_data_final)
        print(f'Predicted Performance: {predicted_performance[0]}')
        performance=predicted_performance
        document = dataset_users.find_one({"user_id": user_id})
        if document:
            # Extract the datasets array from the document
            datasets_value = document.get("datasets", [])
            # Append the new data to the datasets array
            new_data = {
                "course_id": str(course_id),
                "time_spent": str(time_spent),
                "quiz_scores": str(quiz_scores),
                "quiz_attempts": str(quiz_attempts),
                "performance": str(predicted_performance)}
            datasets_value.append(new_data)
            # Update the document with the modified datasets array
            dataset_users.update_one(
                {"user_id": user_id},
                {"$set": {"datasets": datasets_value}})
            print("Document updated successfully.")
        else:
            print("No document found for user_id {}".format(user_id))
        

    else:
        print("No document found for user_id {}".format(user_id))

    return jsonify({"success": True, "score": score, "total_questions": len(correct_answers)})


@app.route('/courses', methods=['GET'])
def get_opted_courses():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username parameter is missing'}), 400
    
    user = users_collection.find_one({'email': username})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    opted_courses = user.get('opted_courses', [])
    print(opted_courses)
    return jsonify({'opted_courses': opted_courses})

@app.route('/playlist_id', methods=['GET'])
def get_playlist_id():
    course_name = request.args.get('courseName')
    course = courses_collection.find_one({'course': "physics"}) #change once playlist ids are added to mongo db
    
    if course:
        print(course['playlist_id'])
        return jsonify({'playlist_id': course['playlist_id']})
    else:
        return jsonify({'error': 'Course not found'}), 404


@app.route('/api/account_details', methods=['POST'])
def account_details():
    email = request.json.get('email')
    print(email)
    userdata = get_username_by_email(email)
    return jsonify({'name': userdata[0],'email':userdata[1]})

def get_username_by_email(email):
    user_data = users_collection.find_one({'email': email})
    print(user_data)

    if user_data:
        return [user_data.get('name'),user_data.get("email")]
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True,port=5000)