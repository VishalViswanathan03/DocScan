import hashlib
from utils.db import get_db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(data):
    """
    Register a new user with optional phone, first_name, last_name, dob.
    """
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone') or None
    first_name = data.get('first_name') or None
    last_name = data.get('last_name') or None
    dob = data.get('dob') or None

    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO users (username, password, role, credits, phone, first_name, last_name, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            hash_password(password),
            'user',
            20,
            phone,
            first_name,
            last_name,
            dob
        ))
        conn.commit()
        return {"message": "User registered successfully"}, 201
    except Exception:
        return {"error": "User already exists or an error occurred."}, 400

def login_user(data):
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    cursor = conn.execute(
        'SELECT * FROM users WHERE username=? AND password=?',
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    if user:
        return {"message": "Login successful", "role": user["role"]}, 200
    return {"error": "Invalid credentials"}, 401

def get_user_profile(username):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return {"error": "User not found"}

def update_user_info(username, data):
    """
    Actually updates phone, first_name, last_name, dob in the DB.
    """
    phone = data.get('phone')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')

    conn = get_db()
    cursor = conn.execute('SELECT username FROM users WHERE username=?', (username,))
    if not cursor.fetchone():
        return {"error": "User not found"}, 404

    conn.execute('''
        UPDATE users
        SET phone = ?, first_name = ?, last_name = ?, dob = ?
        WHERE username = ?
    ''', (phone, first_name, last_name, dob, username))
    conn.commit()
    return {"message": "User info updated successfully"}, 200

def change_password(username, data):
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    conn = get_db()
    cursor = conn.execute('SELECT password FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    if not row:
        return {"error": "User not found"}, 404

    if row["password"] != hash_password(old_password):
        return {"error": "Old password is incorrect"}, 401

    conn.execute('UPDATE users SET password=? WHERE username=?',
                 (hash_password(new_password), username))
    conn.commit()
    return {"message": "Password changed successfully"}, 200
