from utils.db import get_db

def get_admin_analytics():
    conn = get_db()

    cursor = conn.execute('SELECT COUNT(*) as total_scans FROM documents')
    total_scans = cursor.fetchone()["total_scans"]

    cursor = conn.execute('SELECT username, COUNT(*) as scans FROM documents GROUP BY username ORDER BY scans DESC')
    rows = cursor.fetchall()
    top_users = [(r["username"], r["scans"]) for r in rows]

    cursor = conn.execute('SELECT * FROM scan_results')
    scan_rows = cursor.fetchall()

    match_details = []
    for row in scan_rows:
        match_details.append({
            "username": row["username"],
            "doc_id": row["doc_id"],
            "matched_doc_id": row["matched_doc_id"],
            "final_score": row["final_score"],
            "is_similar": row["is_similar"],
            "scanned_at": row["scanned_at"]
        })

    return {
        "total_scans": total_scans,
        "top_users": top_users,
        "match_details": match_details
    }
