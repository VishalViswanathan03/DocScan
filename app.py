from flask import Flask, request, render_template, session, jsonify
from flasgger import Swagger
from utils.db import init_db, get_db
from utils.auth import (
    register_user, login_user, get_user_profile,
    update_user_info, change_password
)
from utils.scanner import scan_document, get_matches
from utils.credits import request_credits
from utils.analytics import get_admin_analytics
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'replace_with_strong_secret_key'

# Add these configurations
app.config['UPLOAD_FOLDER'] = os.path.join('data', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

swagger = Swagger(app)
init_db()

@app.route('/')
def index():
    """
    Home Page
    ---
    responses:
      200:
        description: Renders index.html
    """
    return render_template('index.html')

# ---------------------------
# AUTH ROUTES
# ---------------------------
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
      - name: phone
        in: formData
        type: string
        required: false
      - name: first_name
        in: formData
        type: string
        required: false
      - name: last_name
        in: formData
        type: string
        required: false
      - name: dob
        in: formData
        type: string
        required: false
    responses:
      201:
        description: Registration successful
      400:
        description: Registration error
    """
    data = request.form
    result, status = register_user(data)
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

# ---------------------------
# USER PROFILE & UPDATES
# ---------------------------
@app.route('/user/profile', methods=['GET'])
def profile():
    """
    Get User Profile
    ---
    responses:
      200:
        description: Returns user profile (including phone, first_name, last_name, dob)
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    user_info = get_user_profile(session['username'])
    return jsonify({"profile": user_info})

@app.route('/user/change_password', methods=['POST'])
def user_change_password():
    """
    Change Password
    ---
    parameters:
      - name: old_password
        in: formData
        type: string
        required: true
      - name: new_password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Password changed successfully
      401:
        description: Old password incorrect or user not logged in
      404:
        description: User not found
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.form
    result, status = change_password(session['username'], data)
    return jsonify(result), status

@app.route('/user/update', methods=['PUT'])
def user_update_put():
    """
    Update user info (PUT).
    ---
    parameters:
      - name: phone
        in: formData
        type: string
      - name: first_name
        in: formData
        type: string
      - name: last_name
        in: formData
        type: string
      - name: dob
        in: formData
        type: string
    responses:
      200:
        description: User info updated
      401:
        description: Not logged in
      404:
        description: User not found     
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401

    # Use request.form if you're doing method override or request.data if raw JSON, etc.
    data = request.form
    result, status = update_user_info(session['username'], data)
    return jsonify(result), status

# ---------------------------
# DOCUMENT UPLOAD & MATCH
# ---------------------------
@app.route('/upload', methods=['POST'])
def upload():
    """
    Upload Document
    ---
    parameters:
      - name: document
        in: formData
        type: file
        required: true
    responses:
      200:
        description: Document upload result
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401

    if 'document' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        conn = get_db()
        cursor = conn.execute(
            'INSERT INTO documents (username, filename, content) VALUES (?, ?, ?)',
            (session['username'], filename, content)
        )
        doc_id = cursor.lastrowid
        conn.commit()

        conn.execute('UPDATE users SET credits = credits - 1 WHERE username = ?', (session['username'],))
        conn.commit()

        return jsonify({"success": True, "document_id": doc_id}), 200

    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/health')
def health():
    return "OK", 200

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
    if isinstance(result, dict) and 'matches' in result:
        return render_template('matches.html', matches=result['matches'])
    else:
        return jsonify(result), 404

@app.route('/credits/request', methods=['POST'])
def credits_request():
    """
    Request Additional Credits
    ---
    responses:
      200:
        description: Request success
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = request_credits(session['username'])
    return jsonify(result)

# ---------------------------
# ADMIN ANALYTICS
# ---------------------------
@app.route('/admin/analytics', methods=['GET'])
def admin_analytics():
    """
    Admin Analytics
    ---
    responses:
      200:
        description: Returns analytics data
      401:
        description: Not logged in
      403:
        description: Unauthorized
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    data = get_admin_analytics()
    return jsonify(data)

# ---------------------------
# TEMPLATES
# ---------------------------
@app.route('/page/<name>')
def serve_page(name):
    """
    Render an HTML template by name, e.g. /page/login -> login.html
    """
    return render_template(f"{name}.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
