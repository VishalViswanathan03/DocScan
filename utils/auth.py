import hashlib
from utils.db import get_db

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@12345!"

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
    
    if not username or not password:
        return {"error": "Username and password are required."}, 400
        
    if username == ADMIN_USERNAME:
        if password != ADMIN_PASSWORD:
            return {"error": "Invalid admin password."}, 400
        role = "admin"
        hashed_pw = hash_password(password)
    else:
        role = "user"
        hashed_pw = hash_password(password)
        
    conn = get_db()
    try:
        # Check if the table has password_hash or password column
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Use correct column name based on what exists in the database
        password_column = "password_hash" if "password_hash" in columns else "password"
        
        query = f'''
            INSERT INTO users (username, {password_column}, role, credits, phone, first_name, last_name, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        conn.execute(query, (
            username,
            hashed_pw,
            role,
            20,
            phone,
            first_name,
            last_name,
            dob
        ))
        conn.commit()
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return {"error": "User already exists or an error occurred."}, 400

def login_user(data):
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {"error": "Username and password required"}, 400
    
    conn = get_db()
    
    # Check if the table has password_hash or password column
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Use correct column name based on what exists in the database
    password_column = "password_hash" if "password_hash" in columns else "password"
    
    query = f'SELECT * FROM users WHERE username=? AND {password_column}=?'
    
    cursor = conn.execute(query, (username, hash_password(password)))
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
    
    # Check if the table has password_hash or password column
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Use correct column name based on what exists in the database
    password_column = "password_hash" if "password_hash" in columns else "password"
    
    query = f'SELECT {password_column} FROM users WHERE username=?'
    
    cursor = conn.execute(query, (username,))
    row = cursor.fetchone()
    if not row:
        return {"error": "User not found"}, 404

    if row[password_column] != hash_password(old_password):
        return {"error": "Old password is incorrect"}, 401

    update_query = f'UPDATE users SET {password_column}=? WHERE username=?'
    conn.execute(update_query, (hash_password(new_password), username))
    conn.commit()
    return {"message": "Password changed successfully"}, 200