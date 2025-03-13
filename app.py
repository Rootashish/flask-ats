from flask import Flask, request, jsonify

app = Flask(__name__)  # This initializes the Flask app

database = []  # Temporary storage for applications

@app.route('/')
def home():
    return "Welcome to the ATS System! Use /apply to submit applications."

@app.route('/apply', methods=['POST'])
def apply():
    data = request.json
    applicant = {
        "id": len(database) + 1,
        "name": data.get("name"),
        "email": data.get("email"),
        "resume": data.get("resume"),
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Render requires port 10000
