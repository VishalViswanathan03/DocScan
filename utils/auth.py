import hashlib
from utils.db import get_db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(data):
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password, role, credits) VALUES (?, ?, ?, ?)',
            (username, hash_password(password), 'user', 20)
        )
        conn.commit()
        return {"message": "User registered successfully"}, 201
    except Exception:
        return {"error": "User already exists or error occurred."}, 400

def login_user(data):
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    cursor = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    if user:
        return {"message": "Login successful", "role": user["role"]}, 200
    return {"error": "Invalid credentials"}, 401

def get_user_profile(username):
    conn = get_db()
    cursor = conn.execute(
        'SELECT username, credits, role FROM users WHERE username = ?',
        (username,)
    )
    row = cursor.fetchone()
    if row:
        return dict(row)  # e.g. {"username": "...", "credits": 20, "role": "admin"}
    return {"error": "User not found"}

