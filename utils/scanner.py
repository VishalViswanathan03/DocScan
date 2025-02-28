import os
from utils.db import get_db
from utils.ai_matcher import ai_match

DOCUMENTS_FOLDER = os.path.join('data', 'documents')

def scan_document(username, file):
    if not os.path.exists(DOCUMENTS_FOLDER):
        os.makedirs(DOCUMENTS_FOLDER)
    content = file.read().decode('utf-8')
    filename = file.filename
    path = os.path.join(DOCUMENTS_FOLDER, filename)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    conn = get_db()
    conn.execute(
        'INSERT INTO documents (username, filename, content) VALUES (?, ?, ?)',
        (username, filename, content)
    )
    conn.execute('UPDATE users SET credits = credits - 1 WHERE username = ?', (username,))
    conn.commit()

    return {"message": f"Document '{filename}' uploaded and processed."}

def get_matches(username, doc_id):
    conn = get_db()

    # Fetch the target document
    cursor = conn.execute('SELECT content FROM documents WHERE id = ?', (doc_id,))
    target_doc = cursor.fetchone()
    if not target_doc:
        return {"error": "Document not found"}, 404

    target_content = target_doc["content"]

    # Fetch other documents by same user
    cursor = conn.execute(
        'SELECT id, filename, content FROM documents WHERE username = ? AND id != ?',
        (username, doc_id)
    )
    docs = cursor.fetchall()

    matches = []
    for doc in docs:
        # Basic text overlap
        sim_score = calculate_similarity(target_content, doc["content"])
        # Optional AI
        ai_score = ai_match(target_content, doc["content"])
        final_score = max(sim_score, ai_score)

        # Convert final_score to 1 or 0
        is_similar = 1 if final_score >= 0.5 else 0

        # Insert match record into 'scan_results'
        conn.execute('''
            INSERT INTO scan_results (username, doc_id, matched_doc_id, final_score, is_similar)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, doc_id, doc["id"], final_score, is_similar))

        # Build response
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
