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
import requests
import json
ca = certifi.where()
app = Flask(__name__)
CORS(app)  

# Connect to MongoDB
import urllib
username = urllib.parse.quote_plus("shreyas")
password = urllib.parse.quote_plus("shreyas")



# Create a new client and connect to the server
client = MongoClient("mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority" % (username, password),
                      tlsCAFile=ca)
db = client['learnsync']
users_collection = db['users']
question_collection=db['questions']
courses_collection = db['courses']
dataset_users_collection = db['Dataset_users']
playlists_collection = db['playlists']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        print(data)
        hashed_password = generate_password_hash(data['password'])
        if(data['name']!=''):
            user = {
                'name': data['name'],
                'email': data['email'],
                'password': data['password']
                # 'password':hashed_password
            }
            id =users_collection.insert_one(user)
            print(id)
                    # Insert an empty document with the user's ID into another collection
            other_document = {'user_id': id.inserted_id, 'datasets': [{'course_id': '1', 'time_spent': '55', 'quiz_scores': '19', 'quiz_attempts': '5', 'performance': '0'},
            {'course_id': '1', 'time_spent': '8', 'quiz_scores': '6', 'quiz_attempts': '4', 'performance': '0'},
    {'course_id': '10', 'time_spent': '51', 'quiz_scores': '100', 'quiz_attempts': '2', 'performance': '2'},
    {'course_id': '2', 'time_spent': '6', 'quiz_scores': '54', 'quiz_attempts': '1', 'performance': '1'},
    {'course_id': '2', 'time_spent': '51', 'quiz_scores': '63', 'quiz_attempts': '2', 'performance': '1'},
    {
        "course_id": "1",
        "time_spent": "55",
        "quiz_scores": "19",
        "quiz_attempts": "5",
        "performance": "0"
        },
        {
        "course_id": "1",
        "time_spent": "8",
        "quiz_scores": "33",
        "quiz_attempts": "4",
        "performance": "0"
        },
        {
        "course_id": "7",
        "time_spent": "51",
        "quiz_scores": "99",
        "quiz_attempts": "2",
        "performance": "2"
        },
        {
        "course_id": "2",
        "time_spent": "6",
        "quiz_scores": "99",
        "quiz_attempts": "1",
        "performance": "2"
        },
        {
        "course_id": "2",
        "time_spent": "51",
        "quiz_scores": "99",
        "quiz_attempts": "1",
        "performance": "2"
        },
        {
        "course_id": "3",
        "time_spent": "30",
        "quiz_scores": "50",
        "quiz_attempts": "3",
        "performance": "1"
        },
        {
        "course_id": "3",
        "time_spent": "20",
        "quiz_scores": "80",
        "quiz_attempts": "2",
        "performance": "2"
        },
        {
        "course_id": "4",
        "time_spent": "40",
        "quiz_scores": "90",
        "quiz_attempts": "4",
        "performance": "2"
        },
        {
        "course_id": "5",
        "time_spent": "15",
        "quiz_scores": "60",
        "quiz_attempts": "1",
        "performance": "1"
        },
        {
        "course_id": "5",
        "time_spent": "25",
        "quiz_scores": "75",
        "quiz_attempts": "2",
        "performance": "2"
        },
        {
        "course_id": "6",
        "time_spent": "45",
        "quiz_scores": "85",
        "quiz_attempts": "3",
        "performance": "2"
        },
        {
        "course_id": "8",
        "time_spent": "35",
        "quiz_scores": "75",
        "quiz_attempts": "3",
        "performance": "2"
        },
        {
        "course_id": "9",
        "time_spent": "22",
        "quiz_scores": "60",
        "quiz_attempts": "2",
        "performance": "1"
        },
        {
        "course_id": "10",
        "time_spent": "30",
        "quiz_scores": "95",
        "quiz_attempts": "4",
        "performance": "2"
        },
        {
        "course_id": "11",
        "time_spent": "28",
        "quiz_scores": "70",
        "quiz_attempts": "3",
        "performance": "2"
        },
        {
        "course_id": "12",
        "time_spent": "15",
        "quiz_scores": "50",
        "quiz_attempts": "2",
        "performance": "1"
        },
        {
        "course_id": "13",
        "time_spent": "40",
        "quiz_scores": "85",
        "quiz_attempts": "4",
        "performance": "2"
        },
        {
        "course_id": "14",
        "time_spent": "20",
        "quiz_scores": "60",
        "quiz_attempts": "2",
        "performance": "1"
        },
        {
        "course_id": "15",
        "time_spent": "35",
        "quiz_scores": "75",
        "quiz_attempts": "3",
        "performance": "2"
        },
        {
        "course_id": "16",
        "time_spent": "18",
        "quiz_scores": "40",
        "quiz_attempts": "2",
        "performance": "1"
        },
        {
        "course_id": "17",
        "time_spent": "30",
        "quiz_scores": "95",
        "quiz_attempts": "4",
        "performance": "2"
        },
        {
        "course_id": "18",
        "time_spent": "22",
        "quiz_scores": "60",
        "quiz_attempts": "2",
        "performance": "1"
        },
        {
        "course_id": "19",
        "time_spent": "45",
        "quiz_scores": "85",
        "quiz_attempts": "3",
        "performance": "2"
        },
        {
        "course_id": "20",
        "time_spent": "28",
        "quiz_scores": "70",
        "quiz_attempts": "3",
        "performance": "2"
        },
        {
        "course_id": "21",
        "time_spent": "40",
        "quiz_scores": "25",
        "quiz_attempts": "3",
        "performance": "0"
        },
        {
        "course_id": "22",
        "time_spent": "18",
        "quiz_scores": "15",
        "quiz_attempts": "2",
        "performance": "0"
        },
        ]}
            dataset_users_collection.insert_one(other_document)

            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': "No Details entered"})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
@app.route('/api/gatherinfo', methods=['POST'])
def gatherinfo():
    try:
        data = request.json
        print(data)
        if 'username' not in data:
            return jsonify({'success': False, 'message': "Username not provided"})
        user = users_collection.find_one({'email': data['username']})
        update_data = {
            'college': data.get('college', ''),
            'semester': data.get('semester', ''),
            'branch': data.get('branch', ''),
            'opted_courses': data.get('optedCourses', [])
        }
        users_collection.update_one({'email': data['username']}, {'$set': update_data})
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
            # localStorage.setItem('user_ID', user);
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

courseids={
    "maths":7
}
@app.route('/submit-answers', methods=['POST'])
def submit_answers():
    url = 'http://localhost:3000/predict'

    res = request.get_json()
    submitted_answers = res['answers']
    subject_name = res['testName']
    useremail = res['username']
    user_doc= users_collection.find_one({"email":useremail})
    user_id= user_doc['_id']
    print(type(user_id))
    course_id =courseids[subject_name]
    print(user_id)
    # print(res)

    # Query MongoDB for the correct answers based on the subject name
    correct_answers_data = list(question_collection.find({"subname": subject_name}).limit(len(submitted_answers)))
    correct_answers = [question["answer"] for question in correct_answers_data]
    # print(correct_answers)

    # Evaluate the score
    score = sum(33 for submitted, correct in zip(submitted_answers, correct_answers) if submitted == correct)

    print("Received answers:")
    # for index, answer in enumerate(submitted_answers):
    #     print(f"Question {index + 1}: {answer}")

    print(f"Score: {score} / {len(correct_answers)}")
    subject_doc =courses_collection.find_one({"course": subject_name})
    if subject_doc:
        performance_data = {
            "user_id":user_id,
            "score": score,
            "attempts":1,
            "time_spent":1000,
            # Add more details as needed
        }
        
        courses_collection.update_one(
            {"course": subject_name},
            {"$push": {"performance": performance_data}}
        )
        
        eval_params ={
            'course_id': course_id,
            'timespent': performance_data['time_spent'],
            'quizscore': score,
            'quizzattempts': 1,
            "user_id":str(user_id),
            "course_name":subject_name


        }
        response = requests.post(url, json=eval_params)

        print(f"Performance data appended to subject document: {performance_data}")

    

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
    user_id=user.get('_id')
    print(opted_courses)
    total_recommendations = []
    
    for course_name in opted_courses:
        course_doc = courses_collection.find_one({'course': course_name})
        if course_doc:
            all_performances = course_doc.get('performance',[])
            # print(all_performances)
            specific_performance = next((p for p in all_performances if p['user_id'] == user_id), None)
            print(specific_performance)
            if(specific_performance):
                recommendations = specific_performance['recommendations']
                if(recommendations!=None):
                    for each in recommendations:
                        total_recommendations.append(each)
    # print(total_recommendations)
    if(len(total_recommendations)==0):
        total_recommendations=["Basic ALgebra","Dbms"]
    top_courses_cursor = courses_collection.find().sort("opted_count", -1).limit(3)
    
    # Convert cursor object to a list of dictionaries
    top_courses = list(top_courses_cursor)
    
    top_course_names = [course['course'] for course in top_courses]
    print({'opted_courses': opted_courses,'total_recommendations': total_recommendations,'popular_courses':top_course_names})

    return jsonify({'opted_courses': opted_courses,'total_recommendations': total_recommendations,'popular_courses':top_course_names})

@app.route('/playlist_id', methods=['POST'])
def get_playlist_id():
    data = request.json
    print(data)
    course_name = data['courseName']
    course = playlists_collection.find_one({'playlist_name': course_name}) #change once playlist ids are added to mongo db
    
    if course:
        print(course['playlist_url'])
        return jsonify({'playlist_id': course['playlist_url'],'first_vedio_link':course['first_video_url']})
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
    app.run(port =5000)