from utils.db import get_db
from datetime import datetime

def request_credits(username):
    """
    Submit a credit request for a user.
    """
    conn = get_db()
    # Check if user already has a pending request
    cursor = conn.execute(
        'SELECT id FROM credit_requests WHERE username = ? AND status = "pending"',
        (username,)
    )
    
    if cursor.fetchone():
        return {"error": "You already have a pending credit request"}, 400
    
    conn.execute(
        'INSERT INTO credit_requests (username, amount, status) VALUES (?, 5, "pending")',
        (username,)
    )
    conn.commit()
    return {"message": "Credit request submitted successfully"}, 200

def reset_daily_credits():
    """
    Reset all users' credits to 20.
    """
    conn = get_db()
    conn.execute('UPDATE users SET credits = 20')
    conn.commit()
    return {"message": "Daily credits reset successfully"}, 200

def approve_credit_request(request_id):
    """
    Approve a credit request and add credits to the user's account.
    """
    try:
        conn = get_db()
        cursor = conn.execute(
            'SELECT username, amount FROM credit_requests WHERE id = ? AND status = "pending"',
            (request_id,)
        )
        request = cursor.fetchone()
        
        if not request:
            return False, "Request not found or already processed"
        
        amount = request['amount'] if request['amount'] else 5
        
        conn.execute(
            'UPDATE credit_requests SET status = "approved", processed_at = CURRENT_TIMESTAMP WHERE id = ?',
            (request_id,)
        )
        
        conn.execute(
            'UPDATE users SET credits = credits + ? WHERE username = ?',
            (amount, request['username'])
        )
        
        conn.commit()
        return True, f"Approved {amount} credits for user {request['username']}"
    except Exception as e:
        print(f"Error approving credit request {request_id}: {str(e)}")
        conn.rollback()
        return False, f"Error processing request: {str(e)}"

def reject_credit_request(request_id):
    """
    Reject a credit request without adding credits.
    """
    try:
        conn = get_db()
        cursor = conn.execute(
            'SELECT username FROM credit_requests WHERE id = ? AND status = "pending"',
            (request_id,)
        )
        request = cursor.fetchone()
        
        if not request:
            return False, "Request not found or already processed"
        
        conn.execute(
            'UPDATE credit_requests SET status = "rejected", processed_at = CURRENT_TIMESTAMP WHERE id = ?',
            (request_id,)
        )
        
        conn.commit()
        return True, f"Rejected credit request for user {request['username']}"
    except Exception as e:
        print(f"Error rejecting credit request {request_id}: {str(e)}")
        conn.rollback()
        return False, f"Error processing request: {str(e)}"

def get_user_credits(username):
    """
    Get the current credit balance for a user.
    """
    conn = get_db()
    cursor = conn.execute('SELECT credits FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        return None
    
    return user['credits']