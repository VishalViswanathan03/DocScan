import os
import re
from collections import Counter
import math
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
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')

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

    cursor = conn.execute('SELECT content, filename FROM documents WHERE id = ?', (doc_id,))
    target_doc = cursor.fetchone()
    if not target_doc:
        return {"error": "Document not found"}, 404

    target_content = target_doc["content"]
    target_filename = target_doc["filename"]

    cursor = conn.execute(
        'SELECT id, filename, content FROM documents WHERE username = ? AND id != ?',
        (username, doc_id)
    )
    docs = cursor.fetchall()

    matches = []
    for doc in docs:
        jaccard_sim = calculate_similarity(target_content, doc["content"])
        cosine_sim = calculate_cosine_similarity(target_content, doc["content"])
        
        ai_score = ai_match(target_content, doc["content"])
        
        basic_score = (jaccard_sim + cosine_sim) / 2
        final_score = max(basic_score, ai_score)

        is_similar = 1 if final_score >= 0.5 else 0

        conn.execute('''
            INSERT INTO scan_results (username, doc_id, matched_doc_id, final_score, is_similar)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, doc_id, doc["id"], final_score, is_similar))

        matches.append({
            "id": doc["id"],
            "filename": doc["filename"],
            "similarity": round(final_score, 2),
            "is_similar": is_similar,
            "metrics": {
                "jaccard": round(jaccard_sim, 2),
                "cosine": round(cosine_sim, 2),
                "ai": round(ai_score, 2)
            }
        })

    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)
    
    conn.commit()
    return {"matches": matches, "source": target_filename}


def calculate_similarity(doc1, doc2):
    """
    Calculate Jaccard similarity between two documents
    (improved from the original function)
    """
    doc1 = preprocess_text(doc1)
    doc2 = preprocess_text(doc2)
    
    words1 = set(doc1.split())
    words2 = set(doc2.split())
    
    if not words1 or not words2:
        return 0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0


def calculate_cosine_similarity(doc1, doc2):
    """
    Calculate cosine similarity between two documents using term frequency
    """
    doc1 = preprocess_text(doc1)
    doc2 = preprocess_text(doc2)
    
    # Tokenize
    words1 = doc1.split()
    words2 = doc2.split()
    
    if not words1 or not words2:
        return 0
    
    tf1 = Counter(words1)
    tf2 = Counter(words2)
    
    all_words = set(words1).union(set(words2))
    
    dot_product = sum(tf1.get(word, 0) * tf2.get(word, 0) for word in all_words)
    magnitude1 = math.sqrt(sum(tf1.get(word, 0) ** 2 for word in all_words))
    magnitude2 = math.sqrt(sum(tf2.get(word, 0) ** 2 for word in all_words))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)


def preprocess_text(text):
    """
    Basic text preprocessing for similarity calculation
    """
    if not isinstance(text, str):
        return ""
    
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
