from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)
# Global variable to store aggregated model outputs
global_model_outputs = []

subjects = {
    "physics": {
        0: ["basic physics", "basic maths"],
        1: ["physics", "maths"],
        2: ["advanced physics", "advanced maths"]
    },
    "chemistry": {
        0: ["basic chemistry"],
        1: ["chemistry"],
        2: ["physical chemistry", "organic chemistry"]
    },
    "dbms": {
        0: ["sql basics"],
        1: ["dbms","sql queries"],
        2: ["normalisation in dbms"]
    },
    "kannada": {
        0: ["vyavaharika kannada"],
        1: ["kannada"],
        2: ["aadalitha kannada"]
    },
    "dsa": {
        0: ["basic data types "],
        1: ["dsa algorithms"],
        2: ["Dynamic Programming"]
    },
    "english": {
        0: ["parts of speech","basic grammar in english"],
        1: ["essays"],
        2: ["conversation proficiency in english"]
    },
    "maths": {
        0: ["Algebra"],
        1: ["Probability"],
        2: ["Integration","Advance Algebra"]
    },
    "java": {
        0: ["oops in java"],
        1: ["functions in java"],
        2: ["advanced java programming"]
    },
    "python": {
        0: ["python fundamentals"],
        1: ["python oops"],
        2: ["dsa in python","machine learning using python"]
    },
     "c++": {
        0: ["oops in c++"],
        1: ["functions in c++"],
        2: ["advanced c++ programming"]
    },
    "javascript": {
        0: ["javascript basics"],
        1: ["website using javascript"],
        2: ["node js","express js"]
    }
}

@app.route('/update_predictions', methods=['POST'])
def update_predictions():
    global global_model_outputs

    # Receive predictions from a local client
    local_model_output = request.json['predictions']

    # Append the received predictions to the list of global model outputs
    global_model_outputs.append(local_model_output)

    return 

@app.route('/aggregate_predictions', methods=['GET'])
def aggregate_predictions():
    global global_model_outputs

    # Perform model aggregation (simple averaging)
    if len(global_model_outputs) == 0:
        return jsonify({'message': 'No predictions to aggregate yet.'}), 400
    else:
        aggregated_predictions = np.mean(global_model_outputs, axis=0)

        # Reset the global model outputs for the next aggregation round
        global_model_outputs = []

        return jsonify({'aggregated_predictions': aggregated_predictions.tolist()}), 200

if __name__ == '__main__':
    app.run(debug=True,port=5005)  # Run Flask app in debug mode