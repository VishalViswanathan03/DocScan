import os
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define database path in persistent storage
DB_PATH = os.path.join('data', 'document_scanner.db')

def init_db():
    """Initialize the database with required tables."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    logger.info(f"Initializing database at {os.path.abspath(DB_PATH)}")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info("Database connection established")
        
        conn.execute("PRAGMA foreign_keys = ON")
        
         # Create tables
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            credits INTEGER DEFAULT 10,
            phone TEXT,
            first_name TEXT,
            last_name TEXT,
            dob TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            doc_id INTEGER NOT NULL,
            matched_doc_id INTEGER NOT NULL,
            final_score REAL NOT NULL,
            is_similar INTEGER,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username),
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS credit_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')
        
        cursor = conn.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            # Use the same hash_password function from auth.py for consistency
            from utils.auth import hash_password, ADMIN_USERNAME, ADMIN_PASSWORD
            admin_pass = hash_password(ADMIN_PASSWORD)
            
            conn.execute(
                'INSERT INTO users (username, password_hash, role, credits) VALUES (?, ?, ?, ?)',
                (ADMIN_USERNAME, admin_pass, 'admin', 9999)
            )
            logger.info("Created default admin user")
        
        conn.commit()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_db():
    """Get a database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise