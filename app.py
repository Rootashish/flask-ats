from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import re
import PyPDF2  # For reading PDF resumes
from collections import Counter

app = Flask(__name__)  
CORS(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Limit file size to 5MB

database = []  # Store applications in memory

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF resume."""
    text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() if page.extract_text() else ""
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.lower()  # Convert to lowercase for better matching

def calculate_ats_score(resume_text, job_description):
    """Calculates ATS Score by comparing resume with job description."""
    job_keywords = re.findall(r'\b\w+\b', job_description.lower())  # Extract words
    resume_words = re.findall(r'\b\w+\b', resume_text)

    job_word_count = Counter(job_keywords)
    resume_word_count = Counter(resume_words)

    # Calculate match score
    matched_words = sum(min(resume_word_count[word], job_word_count[word]) for word in job_word_count)
    total_keywords = sum(job_word_count.values())

    if total_keywords == 0:
        return 0  # Avoid division by zero
    return round((matched_words / total_keywords) * 100, 2)  # Percentage score

@app.route('/')
def home():
    return "Welcome to the ATS System! Use /apply to submit applications."

@app.route('/apply', methods=['POST'])
def apply():
    if "resume" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["resume"]
    job_description = request.form.get("job_description", "")  # Get job description

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)  # Save resume

        resume_text = extract_text_from_pdf(file_path)  # Extract text
        ats_score = calculate_ats_score(resume_text, job_description)  # Calculate score

        applicant = {
            "id": len(database) + 1,
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "resume": f"/uploads/{file.filename}",
            "status": "Pending",
            "ats_score": ats_score  # Store ATS score
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  
