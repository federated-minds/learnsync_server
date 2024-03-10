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
                for each in recommendations:
                    total_recommendations.append(each)
    # print(total_recommendations)
    top_courses_cursor = courses_collection.find().sort("opted_count", -1).limit(3)
    
    # Convert cursor object to a list of dictionaries
    top_courses = list(top_courses_cursor)
    
    top_course_names = [course['course'] for course in top_courses]
    print(top_course_names)

    return jsonify({'opted_courses': opted_courses,'total_recommendations': total_recommendations,'popular_courses':top_course_names})

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
    app.run()