from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)  
CORS(app)  # Enable CORS for frontend communication

# Configure upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Limit file size to 5MB

database = []  # Temporary in-memory storage

@app.route('/')
def home():
    return """
    <h2>Welcome to the ATS System!</h2>
    <p>Use the form below to submit applications.</p>
    <form action="/apply" method="post" enctype="multipart/form-data">
        <label>Name:</label> <input type="text" name="name"><br>
        <label>Email:</label> <input type="email" name="email"><br>
        <label>Resume:</label> <input type="file" name="resume"><br>
        <input type="submit" value="Apply">
    </form>
    """

@app.route('/apply', methods=['POST'])
def apply():
    if "resume" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)  # Save the file

        applicant = {
            "id": len(database) + 1,
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "resume": f"/uploads/{file.filename}",  # Store relative path
            "status": "Pending"
        }
        database.append(applicant)
        return jsonify({"message": "Application submitted", "applicant": applicant}), 201

@app.route('/applicants', methods=['GET'])
def get_applicants():
    return jsonify(database)

@app.route('/update_status/<int:applicant_id>', methods=['PUT'])
def update_status(applicant_id):
    data = request.json
    for applicant in database:
        if applicant["id"] == applicant_id:
            applicant["status"] = data.get("status", applicant["status"])
            return jsonify({"message": "Status updated", "applicant": applicant})
    return jsonify({"error": "Applicant not found"}), 404

# Route to serve uploaded resumes
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  
