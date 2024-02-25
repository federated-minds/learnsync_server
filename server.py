
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  

# Connect to MongoDB
import urllib
username = urllib.parse.quote_plus("jaswanth")
password = urllib.parse.quote_plus("J@ssu007")



# Create a new client and connect to the server
client = MongoClient("mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority"%(username,password))
db = client['learnsync']
users_collection = db['users']
question_collection=db['questions']
courses_collection = db['courses']

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
            'password': data['password']
            # 'password':hashed_password
        }
        id =users_collection.insert_one(user)
        print(id)
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
    app.run(debug=True)