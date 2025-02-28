from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flasgger import Swagger
from utils.auth import register_user, login_user, get_user_profile
from utils.scanner import scan_document, get_matches
from utils.credits import request_credits
from utils.analytics import get_admin_analytics
from utils.db import init_db

app = Flask(__name__)
app.secret_key = 'replace_with_strong_secret_key'

# Initialize Swagger
swagger = Swagger(app)

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    """
    Home Page
    ---
    responses:
      200:
        description: Renders the home page (index.html)
    """
    return render_template('index.html')

@app.route('/auth/register', methods=['POST'])
def register():
    """
    User Registration
    ---
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      201:
        description: User created
      400:
        description: Registration error
    """
    data = request.form
    result, status = register_user(data)
    if status == 201:
        return jsonify({"success": True, "message": "Registration successful"}), 201
    return jsonify(result), status

@app.route('/auth/login', methods=['POST'])
def login():
    """
    User Login
    ---
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.form
    result, status = login_user(data)
    if status == 200:
        session['username'] = data.get('username')
        session['role'] = result.get('role', 'user')
        return jsonify({"success": True, "role": session['role']}), 200
    return jsonify(result), status

@app.route('/auth/logout', methods=['POST'])
def logout():
    """
    User Logout
    ---
    responses:
      200:
        description: Logout successful
    """
    session.clear()
    return jsonify({"success": True, "message": "Logged out"}), 200

@app.route('/user/profile', methods=['GET'])
def profile():
    """
    User Profile
    ---
    responses:
      200:
        description: Returns user profile (credits, username)
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    profile_data = get_user_profile(session['username'])
    return jsonify({"profile": profile_data}), 200

@app.route('/upload', methods=['POST'])
def upload():
    """
    Document Upload
    ---
    parameters:
      - name: document
        in: formData
        type: file
        required: true
    responses:
      200:
        description: Returns JSON with upload result
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    file = request.files.get('document')
    result = scan_document(session['username'], file)
    return jsonify(result)

@app.route('/matches/<int:doc_id>', methods=['GET'])
def matches(doc_id):
    """
    Document Matching
    ---
    parameters:
      - name: doc_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Matching documents
      401:
        description: Not logged in
      404:
        description: Document not found
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = get_matches(session['username'], doc_id)
    return jsonify(result)

@app.route('/credits/request', methods=['POST'])
def credits_request():
    """
    Request Additional Credits
    ---
    responses:
      200:
        description: Returns JSON with success message
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = request_credits(session['username'])
    return jsonify(result)

@app.route('/admin/analytics', methods=['GET'])
def admin_analytics():
    """
    Admin Analytics
    ---
    responses:
      200:
        description: Returns admin analytics
      403:
        description: Unauthorized
    """
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    analytics = get_admin_analytics()
    return jsonify(analytics), 200

@app.route('/page/<name>')
def pages(name):
    """
    Render HTML pages
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Renders the requested HTML template
    """
    # For example: /page/login -> templates/login.html
    return render_template(f"{name}.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
