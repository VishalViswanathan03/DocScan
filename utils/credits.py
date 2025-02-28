from utils.db import get_db

def request_credits(username):
    conn = get_db()
    conn.execute(
        'INSERT INTO credit_requests (username) VALUES (?)',
        (username,)
    )
    conn.commit()
    return {"message": "Credit request submitted"}

def reset_daily_credits():
    conn = get_db()
    conn.execute('UPDATE users SET credits = 20')
    conn.commit()
