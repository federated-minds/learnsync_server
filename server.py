
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

if __name__ == '__main__':
    app.run()