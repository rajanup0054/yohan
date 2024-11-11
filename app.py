from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import pickle
import os

# Load the trained model
with open("model.pkl", "rb") as file:
    model = pickle.load(file)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Sample courses based on engagement level predictions
course_recommendations = {
    0: ["Introductory Math", "Basic English", "Fundamentals of Science"],
    1: ["Intermediate Algebra", "Essay Writing", "General Science"],
    2: ["Advanced Calculus", "Literature Analysis", "Physics Principles"]
}

# Route to upload the Excel file
@app.route('/')
def home():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file is part of the request
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        
        # If no file is selected, redirect to the home page
        if file.filename == '':
            return redirect(request.url)
        
        # Read the Excel file
        df = pd.read_excel(file)

        # Ensure the required columns exist in the uploaded file
        required_columns = ['Name', 'interaction_count', 'quiz_scores', 'completion_rate', 'parent_email']
        if not all(col in df.columns for col in required_columns):
            return "Missing required columns in the file"

        # Store the student data in session
        session['students'] = df.to_dict(orient='records')

        return render_template("student_list.html", students=session['students'])
    except Exception as e:
        return f"An error occurred: {e}"

# Route to view the recommended courses for a specific student
@app.route('/view/<student_name>')
def view(student_name):
    try:
        # Retrieve students data from session
        students = session.get('students', [])

        # Find the student in the list
        student = next(student for student in students if student['Name'] == student_name)

        # Prepare the data for the model prediction
        student_data = pd.DataFrame([[student['interaction_count'], student['quiz_scores'], student['completion_rate']]],
                                    columns=["interaction_count", "quiz_scores", "completion_rate"])

        # Predict the engagement level
        engagement_level = model.predict(student_data)[0]

        # Get recommended courses based on engagement level
        recommended_courses = course_recommendations[engagement_level]

        return render_template("view_student.html", student=student, recommended_courses=recommended_courses)
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)