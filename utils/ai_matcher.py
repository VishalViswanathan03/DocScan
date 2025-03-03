import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer

def initialize_nltk():
    """Ensure all required NLTK data is downloaded"""
    required_resources = ['punkt', 'stopwords', 'punkt_tab']
    for resource in required_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource)

initialize_nltk()

try:
    from sentence_transformers import SentenceTransformer
    HAVE_TRANSFORMERS = True
except ImportError:
    HAVE_TRANSFORMERS = False
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
        HAVE_SKLEARN = True
    except ImportError:
        HAVE_SKLEARN = False

_model = None

def get_model():
    """
    Initialize and return the model, loading it only once
    """
    global _model
    if HAVE_TRANSFORMERS and _model is None:
        try:
            _model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading transformer model: {e}")
    
    return _model

def ai_match(doc1, doc2):
    """
    Perform AI-based similarity matching between two documents.
    Returns a similarity score between 0 and 1.
    """
    if not isinstance(doc1, str) or not isinstance(doc2, str):
        return 0.0
    
    if not doc1.strip() or not doc2.strip():
        return 0.0
    
    doc1_clean = preprocess_text(doc1)
    doc2_clean = preprocess_text(doc2)
    
    transformer_sim = transformer_similarity(doc1_clean, doc2_clean)
    if transformer_sim is not None:
        return transformer_sim
    
    if HAVE_SKLEARN:
        return tfidf_similarity(doc1_clean, doc2_clean)
    
    return custom_tfidf_similarity(doc1_clean, doc2_clean)

def transformer_similarity(doc1, doc2, chunk_size=1000, overlap=200):
    """
    Calculate semantic similarity using transformer model.
    Handles long documents by chunking.
    """
    model = get_model()
    if model is None:
        return None
    
    try:
        doc1_chunks = chunk_text(doc1, chunk_size, overlap)
        doc2_chunks = chunk_text(doc2, chunk_size, overlap)
        
        embeddings1 = model.encode(doc1_chunks)
        embeddings2 = model.encode(doc2_chunks)
        
        best_similarity = 0
        for emb1 in embeddings1:
            for emb2 in embeddings2:
                similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                best_similarity = max(best_similarity, similarity)
        
        return float(best_similarity)
    except Exception as e:
        print(f"Transformer similarity error: {e}")
        return None

def tfidf_similarity(doc1, doc2):
    """
    Calculate TF-IDF cosine similarity using sklearn
    """
    try:
        vectorizer = TfidfVectorizer()
        
        tfidf_matrix = vectorizer.fit_transform([doc1, doc2])
        
        similarity = sklearn_cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    except Exception as e:
        print(f"TF-IDF similarity error: {e}")
        return custom_tfidf_similarity(doc1, doc2)

def custom_tfidf_similarity(doc1, doc2):
    """
    Custom implementation of TF-IDF similarity without external libraries
    """
    words1 = doc1.split()
    words2 = doc2.split()
    
    all_words = set(words1 + words2)
    doc_freq = {}
    for word in all_words:
        doc_freq[word] = (1 if word in words1 else 0) + (1 if word in words2 else 0)
    
    vector1 = {}
    vector2 = {}
    
    word_count1 = len(words1) or 1  
    word_count2 = len(words2) or 1
    
    for word in all_words:
        tf1 = words1.count(word) / word_count1
        tf2 = words2.count(word) / word_count2
        
        idf = 1.0 / doc_freq[word] if doc_freq[word] > 0 else 0
        
        vector1[word] = tf1 * idf
        vector2[word] = tf2 * idf
    
    dot_product = sum(vector1.get(word, 0) * vector2.get(word, 0) for word in all_words)
    magnitude1 = np.sqrt(sum(value ** 2 for value in vector1.values()))
    magnitude2 = np.sqrt(sum(value ** 2 for value in vector2.values()))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def preprocess_text(text):
    """
    Comprehensive text preprocessing:
    - Remove special characters
    - Convert to lowercase
    - Remove stopwords
    - Apply stemming
    """
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    tokens = word_tokenize(text)
    
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
    
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]
    
    return ' '.join(tokens)

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split long text into overlapping chunks for processing
    """
    if len(text) < chunk_size:
        return [text]
    
    sentences = sent_tokenize(text)
    
    if len(sentences) < 3:
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_length = len(sentence_words)
        
        if current_length + sentence_length <= chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            if current_length > 0 and overlap > 0:
                overlap_size = 0
                overlap_chunk = []
                
                for s in reversed(current_chunk):
                    s_len = len(s.split())
                    if overlap_size + s_len <= overlap:
                        overlap_chunk.insert(0, s)
                        overlap_size += s_len
                    else:
                        break
                
                current_chunk = overlap_chunk
                current_length = overlap_size
            else:
                current_chunk = []
                current_length = 0
            
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks