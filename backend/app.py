import face_recognition
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from models import SessionLocal, Student, AttendanceLog

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize the database session
db = SessionLocal()

# Load student photos and encode faces from the database
known_face_encodings = []
known_face_names = []

students = db.query(Student).all()
for student in students:
    try:
        image = face_recognition.load_image_file(student.photo)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(student.name)
    except IndexError:
        print(f"Warning: No face found in {student.photo}. Skipping this image.")

@app.route("/process_frame", methods=["POST"])
def process_frame():
    """Process a frame uploaded from the frontend."""
    file = request.files.get("frame")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        frame = face_recognition.load_image_file(file)
        face_encodings = face_recognition.face_encodings(frame)

        students_present = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in matches:
                match_index = matches.index(True)
                students_present.append(known_face_names[match_index])

        # Log attendance to the database
        for student in students_present:
            attendance_log = AttendanceLog(student_name=student, timestamp=str(datetime.now()))
            db.add(attendance_log)

        db.commit()

        return jsonify({"students": students_present})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_student", methods=["POST"])
def add_student():
    """Add a new student to the database."""
    name = request.form.get("name")
    photo_file = request.files.get("photo")

    if not name or not photo_file:
        return jsonify({"error": "Name and photo file are required"}), 400

    try:
        # Save the uploaded photo
        photo_path = os.path.join("student_photos", photo_file.filename)
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        photo_file.save(photo_path)

        # Add the student to the database
        new_student = Student(name=name, photo=photo_path)
        db.add(new_student)
        db.commit()

        # Update the known faces list
        image = face_recognition.load_image_file(photo_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(name)

        return jsonify({"message": "Student added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        db.close()
