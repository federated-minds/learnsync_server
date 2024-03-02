from flask import Flask, jsonify,request
from pymongo import MongoClient
import numpy as np
from scipy.stats import percentileofscore

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
collection = db['your_collection']

@app.route('/aggregate_performance', methods=['GET'])
def aggregate_performance():
    try:
        # Retrieve all documents from the collection
        cursor = collection.find({})
        performances = [doc['performance'] for doc in cursor]

        # Calculate aggregate performance
        total = len(performances)
        bad_count = sum(1 for p in performances if p == 0)
        avg_count = sum(1 for p in performances if p == 1)
        good_count = sum(1 for p in performances if p == 2)

        # Calculate percentages
        bad_percentage = (bad_count / total) * 100
        avg_percentage = (avg_count / total) * 100
        good_percentage = (good_count / total) * 100

        # Calculate relative performance and percentile for each user
        relative_performances = []
        percentiles = []
        for i, doc in enumerate(cursor):
            performance = doc['performance']
            relative_performance = (performance - np.mean(performances)) / np.std(performances)
            relative_performances.append(relative_performance)

            # Calculate percentile
            percentile = percentileofscore(performances, performance)
            percentiles.append(percentile)

            # Update user's document with relative performance and percentile
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {
                    'relative_performance': relative_performance,
                    'percentile': percentile
                }}
            )

        # Return aggregate performance as JSON
        aggregate_performance = {
            'total': total,
            'bad_percentage': bad_percentage,
            'avg_percentage': avg_percentage,
            'good_percentage': good_percentage
        }
        return jsonify(aggregate_performance)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    
    
    
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
users_collection = db['users']
recommendations_dict = {
    'good': 'Keep up the good work! Continue to strive for excellence.',
    'average': 'You are doing well, but there is room for improvement. Consider focusing more on your weaker areas.',
    'poor': 'Your performance needs improvement. Focus on understanding the concepts better and practicing more.'
}

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    try:
        # Get user ID from the query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required in the query parameters'}), 400

        # Retrieve user's details from the users collection
        user = users_collection.find_one({'user_id': user_id})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get course performance details
        course_performance = user.get('course_performance', [])

        # Generate recommendations for each course
        recommendations = {}
        for course_info in course_performance:
            performance = course_info.get('predicted', 0)

            # Classify performance for the current subject
            performance_category = classify_performance(performance)

            # Get recommendation based on performance category
            recommendation = recommendations_dict.get(performance_category)

            # Store recommendation for the current subject
            recommendations[course_info.get('subject_name')] = recommendation

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def classify_performance(performance):
    # Logic to classify performance based on performance value
    if performance >= 80:
        return 'good'
    elif performance >= 60:
        return 'average'
    else:
        return 'poor'


if __name__ == '__main__':
    app.run(debug=True,port=5003)
