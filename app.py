from flask import Flask, request, jsonify, session
from flasgger import Swagger
from utils.db import init_db, get_db
from utils.auth import register_user, login_user, get_user_profile
from utils.scanner import scan_document, get_matches
from utils.credits import request_credits
from utils.analytics import get_admin_analytics

app = Flask(__name__)
app.secret_key = 'replace_with_strong_secret_key'

swagger = Swagger(app)  # Enable Swagger docs at /apidocs

# Initialize SQLite DB on startup
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

# --------------------------------
# AUTH: Register, Login, Logout
# --------------------------------
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
        description: Registration success
      400:
        description: Registration error
    """
    form_data = request.form
    result, status = register_user(form_data)
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
        description: Login success
      401:
        description: Invalid credentials
    """
    form_data = request.form
    result, status = login_user(form_data)
    if status == 200:
        session['username'] = form_data.get('username')
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
        description: Logout success
    """
    session.clear()
    return jsonify({"success": True, "message": "Logged out"}), 200

# --------------------------------
# USER/UPLOAD: Profile, Upload
# --------------------------------
@app.route('/user/profile', methods=['GET'])
def profile():
    """
    Get User Profile
    ---
    responses:
      200:
        description: Returns user profile
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
        description: Document upload result
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
        description: Credit request success
      401:
        description: Not logged in
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = request_credits(session['username'])
    return jsonify(result)



@app.route('/make_admin/<username>', methods=['POST'])
def make_admin(username):
    """
    Promote user to admin role, requiring a secret code in the request body.
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
      - name: secret_code
        in: formData
        type: string
        required: true
    responses:
      200:
        description: User is now admin
      401:
        description: Invalid or missing secret code
      404:
        description: User not found
    """
    # Replace 'my_super_secret_code' with something more secure
    required_code = 'my_super_secret_code'

    # The form data must include "secret_code"
    provided_code = request.form.get('secret_code')
    if provided_code != required_code:
        return jsonify({"error": "Unauthorized - invalid code"}), 401

    # Check if user exists
    conn = get_db()
    cursor = conn.execute("SELECT username FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": f"User '{username}' not found"}), 404

    # Update role
    conn.execute("UPDATE users SET role='admin' WHERE username=?", (username,))
    conn.commit()
    return jsonify({"message": f"User '{username}' is now admin"}), 200

# --------------------------------
# ADMIN
# --------------------------------
@app.route('/admin/analytics', methods=['GET'])
def admin_analytics():
    """
    Admin Analytics
    ---
    responses:
      200:
        description: Admin analytics data
      401:
        description: Not logged in
      403:
        description: Unauthorized
    """
    # Check if there's a user logged in
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401

    # Retrieve user info from DB
    user_info = get_user_profile(session['username'])
    if not user_info or user_info.get('error'):
        return jsonify({"error": "User not found"}), 404

    # Ensure the user is actually admin
    if user_info.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # If we get here, user is admin
    data = get_admin_analytics()
    return jsonify(data), 200


# --------------------------------
# TEMPLATES
# --------------------------------
@app.route('/page/<name>')
def serve_page(name):
    """Renders the requested page from templates."""
    return render_template(f"{name}.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
