from flask import Flask, request, render_template
import pickle
import pandas as pd
import numpy as np

# Load the trained model
with open("model.pkl", "rb") as file:
    model = pickle.load(file)

app = Flask(__name__)

# Sample courses based on engagement level predictions
course_recommendations = {
    0: ["Introductory Math", "Basic English", "Fundamentals of Science"],
    1: ["Intermediate Algebra", "Essay Writing", "General Science"],
    2: ["Advanced Calculus", "Literature Analysis", "Physics Principles"]
}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input data from form
        interaction_count = int(request.form.get("interaction_count"))
        quiz_scores = float(request.form.get("quiz_scores"))
        completion_rate = float(request.form.get("completion_rate"))

        # Create a DataFrame for the model
        student_data = pd.DataFrame([[interaction_count, quiz_scores, completion_rate]],
                                    columns=["interaction_count", "quiz_scores", "completion_rate"])

        # Predict engagement level
        engagement_level = model.predict(student_data)[0]

        # Get recommended courses based on engagement level
        recommended_courses = course_recommendations[engagement_level]

        return render_template("result.html", engagement_level=engagement_level,
                               recommended_courses=recommended_courses)
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
