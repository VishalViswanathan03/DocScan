import os
from utils.db import get_db
from utils.ai_matcher import ai_match
from werkzeug.utils import secure_filename
from flask import current_app

DOCUMENTS_FOLDER = os.path.join('data', 'documents')

def scan_document(username, file):
    conn = get_db()
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        file.save(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        cursor = conn.execute(
            'INSERT INTO documents (username, filename, content) VALUES (?, ?, ?)',
            (username, filename, content))
        doc_id = cursor.lastrowid
        conn.commit()
        
        conn.execute('UPDATE users SET credits = credits - 1 WHERE username = ?', (username,))
        conn.commit()
        
        return {"success": True, "document_id": doc_id}
    except Exception as e:
        print(f"Upload Error: {e}")
        return {"error": str(e)}


def get_matches(username, doc_id):
    conn = get_db()

    cursor = conn.execute('SELECT content FROM documents WHERE id = ?', (doc_id,))
    target_doc = cursor.fetchone()
    if not target_doc:
        return {"error": "Document not found"}, 404

    target_content = target_doc["content"]

    cursor = conn.execute(
        'SELECT id, filename, content FROM documents WHERE username = ? AND id != ?',
        (username, doc_id)
    )
    docs = cursor.fetchall()

    matches = []
    for doc in docs:
        sim_score = calculate_similarity(target_content, doc["content"])
        ai_score = ai_match(target_content, doc["content"])
        final_score = max(sim_score, ai_score)

        is_similar = 1 if final_score >= 0.5 else 0

        conn.execute('''
            INSERT INTO scan_results (username, doc_id, matched_doc_id, final_score, is_similar)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, doc_id, doc["id"], final_score, is_similar))

        matches.append({
            "id": doc["id"],
            "filename": doc["filename"],
            "similarity": round(final_score, 2),
            "is_similar": is_similar
        })

    conn.commit()
    return {"matches": matches}


def calculate_similarity(doc1, doc2):
    words1 = set(doc1.split())
    words2 = set(doc2.split())
    if not words1 or not words2:
        return 0
    return len(words1 & words2) / len(words1 | words2)
