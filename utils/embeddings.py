from sentence_transformers import SentenceTransformer
import numpy as np
from utils.pdf_parser import split_into_chunks
import os
import pickle
import hashlib

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Add caching for embeddings to improve performance
def generate_embeddings(text, cache_dir="cache/embeddings"):
    """Generate embeddings with caching for performance"""
    # Create hash of the text for cache key
    text_hash = hashlib.md5(text.encode()).hexdigest()
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{text_hash}.pkl")
    
    # Try to load from cache first
    if os.path.exists(cache_path):
        print(f"Loading embeddings from cache")
        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Cache loading error: {str(e)}")
    
    # If cache miss or error, generate embeddings
    print(f"Generating new embeddings")
    
    # Ensure text is a string
    if isinstance(text, list):
        text = ' '.join(text)
    elif not isinstance(text, str):
        text = str(text)
    
    # Split text into chunks
    print(f"About to call split_into_chunks on text of type: {type(text)}")
    chunks = split_into_chunks(text)
    
    # Generate embeddings for each chunk
    embeddings = model.encode(chunks)
    
    result = {
        'chunks': chunks,
        'embeddings': embeddings
    }
    
    # Save to cache
    try:
        with open(cache_path, "wb") as f:
            pickle.dump(result, f)
    except Exception as e:
        print(f"Cache saving error: {str(e)}")
    
    return result

def generate_query_embedding(query):
    """
    Generate embedding for a query string
    
    Args:
        query: Query text
        
    Returns:
        numpy.ndarray: Embedding vector for the query
    """
    return model.encode([query])[0]