
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to MongoDB
import urllib
username = urllib.parse.quote_plus("jaswanth")
password = urllib.parse.quote_plus("J@ssu007")



# Create a new client and connect to the server
client = MongoClient("mongodb+srv://%s:%s@cluster0.r3jv8jx.mongodb.net/?retryWrites=true&w=majority"%(username,password))
db = client['learnsync']
users_collection = db['users']
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
    {"name": "Test 1", "time": "10:00 AM", "date": "2024-02-16"},
    {"name": "Test 2", "time": "11:30 AM", "date": "2024-02-17"},
    {"name": "Test 3", "time": "02:00 PM", "date": "2024-02-18"},
]
@app.route("/tests")
def get_tests():
    return jsonify(tests)


# Dummy data for questions
questions_data = {
    "Test 1": ["What is your name?", "What is your age?", "Where are you from?"],
    "Test 2": ["What is 2 + 2?", "What is the capital of France?", "Who wrote Romeo and Juliet?"],
    "Test 3": ["What is the chemical symbol for water?", "Who painted the Mona Lisa?", "What is the tallest mountain in the world?"],
}

@app.route("/questions")
def get_questions():
    test_name = request.args.get("test_name")
    if test_name not in questions_data:
        return jsonify({"error": "Test not found"}), 404
    return jsonify(questions_data[test_name])


if __name__ == '__main__':
    app.run(debug=True)