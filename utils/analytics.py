from utils.db import get_db

def get_admin_analytics():
    conn = get_db()
    cursor = conn.execute('SELECT COUNT(*) as total_scans FROM documents')
    total_scans = cursor.fetchone()["total_scans"]

    cursor = conn.execute('SELECT username, COUNT(*) as scans FROM documents GROUP BY username ORDER BY scans DESC')
    rows = cursor.fetchall()

    return {
        "total_scans": total_scans,
        "top_users": [(r["username"], r["scans"]) for r in rows]
    }
