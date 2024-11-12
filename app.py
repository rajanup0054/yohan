from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import pandas as pd
import pickle
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Load the trained model
with open("model.pkl", "rb") as file:
    model = pickle.load(file)

# Sample courses based on engagement level predictions
course_recommendations = {
    0: ["Introductory Math", "Basic English", "Fundamentals of Science"],
    1: ["Intermediate Algebra", "Essay Writing", "General Science"],
    2: ["Advanced Calculus", "Literature Analysis", "Physics Principles"]
}

# Root route redirecting to upload page
@app.route('/')
def home():
    return redirect(url_for('upload_file'))

# Route for file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            students_df = pd.read_excel(file)
            students_df.to_csv("students.csv", index=False)  # Save for reference
            students = []
            for _, row in students_df.iterrows():
                student_data = {
                    "Name": row['Name'],
                    "interaction_count": row['interaction_count'],
                    "quiz_scores": row['quiz_scores'],
                    "completion_rate": row['completion_rate'],
                    "parent_email": row['parent_email']
                }
                students.append(student_data)
            return render_template('student_list.html', students=students)
    return render_template('upload.html')

# Route for student details view
@app.route('/view_student/<student_name>')
def view_student(student_name):
    students_df = pd.read_csv("students.csv")
    student_data = students_df[students_df["Name"] == student_name].iloc[0].to_dict()
    student_df = pd.DataFrame([[student_data['interaction_count'], student_data['quiz_scores'], student_data['completion_rate']]],
                              columns=["interaction_count", "quiz_scores", "completion_rate"])
    engagement_level = model.predict(student_df)[0]
    recommended_courses = course_recommendations[engagement_level]
    return render_template("view_student.html", student_data=student_data, recommended_courses=recommended_courses)

# Route to download performance card
@app.route('/download_card/<student_name>')
def download_card(student_name):
    students_df = pd.read_csv("students.csv")
    student_data = students_df[students_df["Name"] == student_name].iloc[0].to_dict()
    
    card_content = f"""
    Performance Card for {student_name}
    ---------------------------------
    Interaction Count: {student_data['interaction_count']}
    Quiz Scores: {student_data['quiz_scores']}
    Completion Rate: {student_data['completion_rate']}
    Parent Email: {student_data['parent_email']}
    """
    card_file = f"{student_name}_performance_card.txt"
    with open(card_file, "w") as f:
        f.write(card_content)
    
    return send_file(card_file, as_attachment=True)

# Route to send email
@app.route('/send_email/<student_name>')
def send_email(student_name):
    students_df = pd.read_csv("students.csv")
    student_data = students_df[students_df["Name"] == student_name].iloc[0].to_dict()
    parent_email = student_data["parent_email"]
    try:
        sender_email = "akumarnayak50@gmail.com"
        sender_password = "qvjthqhfwzpeyyvh"
        subject = f"Performance Update for {student_name}"
        body = f"""
        Dear Parent,

        Please find below the performance update for {student_name}:
        Interaction Count: {student_data['interaction_count']}
        Quiz Scores: {student_data['quiz_scores']}
        Completion Rate: {student_data['completion_rate']}
        
        Regards,
        School Administration
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = parent_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, parent_email, msg.as_string())

        return jsonify({"status": f"Email sent successfully to {parent_email}"})
    except Exception as e:
        return jsonify({"status": f"Failed to send email: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
