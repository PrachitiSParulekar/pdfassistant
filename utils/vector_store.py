import faiss
import numpy as np
import os
import pickle
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    """
    A vector store implementation using FAISS
    """
    
    def __init__(self, dimension=384, store_path='./data/vector_store.pkl'):  # default dimension for 'all-MiniLM-L6-v2'
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = {}  # doc_id -> {chunks, metadata}
        self.doc_ids = []  # To maintain the order of documents
        self.store_path = store_path
        self._ensure_directory_exists()
        self.load()
        
    def _ensure_directory_exists(self):
        """Create directory for the vector store if it doesn't exist."""
        directory = os.path.dirname(self.store_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory for vector store: {directory}")
    
    def _add_document_legacy(self, doc_id, text, embedding_data):
        """
        Legacy add document method (for backward compatibility)
        
        Args:
            doc_id: Unique identifier for the document
            text: Original text of the document
            embedding_data: Dict containing 'chunks' and 'embeddings'
        """
        chunks = embedding_data['chunks']
        embeddings = embedding_data['embeddings']
        
        # Store document info
        self.documents[doc_id] = {
            'text': text,
            'chunks': chunks,
            'chunk_start_idx': len(self.doc_ids)
        }
        
        # Add embeddings to FAISS index
        embeddings_np = np.array(embeddings).astype('float32')
        self.index.add(embeddings_np)
        
        # Track document IDs for each embedding
        for _ in range(len(chunks)):
            self.doc_ids.append(doc_id)
    
    def search(self, query_embedding, top_k=5, threshold=None):
        """
        Search the vector store for similar chunks
        
        Args:
            query_embedding: Embedding vector for the query
            top_k: Number of results to return
            
        Returns:
            list: List of (doc_id, chunk_text, similarity_score) tuples
        """
        # Format query embedding
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Handle empty index case
        if self.index.ntotal == 0:
            return []
            
        # Search the index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.doc_ids):
                continue  # Skip invalid indices
                
            doc_id = self.doc_ids[idx]
            if doc_id not in self.documents:
                continue  # Skip if document doesn't exist
                
            # Calculate relative chunk index with bounds checking
            relative_idx = idx - self.documents[doc_id]['chunk_start_idx']
            chunks = self.documents[doc_id]['chunks']
            
            if relative_idx < 0 or relative_idx >= len(chunks):
                continue  # Skip if chunk index is out of range
                
            chunk_text = chunks[relative_idx]
            results.append({
                'doc_id': doc_id,
                'chunk': chunk_text,
                'score': float(distances[0][i])
            })
        
        if threshold is not None:
            results = [r for r in results if r['score'] <= threshold]
        return results
    
    def similarity_search(self, query_embedding, k=5, threshold=None):
        """
        Alias for search method to maintain compatibility
        
        Args:
            query_embedding: Embedding vector for the query
            k: Number of results to return (equivalent to top_k in search)
            
        Returns:
            list: List of results from the search method
        """
        return self.search(query_embedding, top_k=k, threshold=threshold)
    
    def save(self):
        """Save the vector store to disk."""
        try:
            with open(self.store_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'doc_ids': self.doc_ids,
                    'index': faiss.serialize_index(self.index)
                }, f)
            logger.info(f"Vector store saved with {len(self.doc_ids)} entries")
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
    
    def load(self):
        """Load the vector store from disk."""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', {})
                    self.doc_ids = data.get('doc_ids', [])
                    if 'index' in data:
                        self.index = faiss.deserialize_index(data['index'])
                logger.info(f"Vector store loaded with {len(self.doc_ids)} entries")
            except Exception as e:
                logger.error(f"Failed to load vector store: {str(e)}")                # Initialize empty store on error
                self.documents = {}
                self.doc_ids = []
        else:
            logger.info("No vector store found, starting with empty store")
    
    def remove_document(self, doc_id):
        """
        Remove a document and its chunks from the vector store
        
        Args:
            doc_id: ID of the document to remove
            
        Returns:
            bool: True if document was removed, False if not found
        """
        if doc_id not in self.documents:
            logger.warning(f"Document {doc_id} not found in vector store")
            return False
        
        # Remove from documents dictionary
        del self.documents[doc_id]
        
        # For now, we'll keep the embeddings in the index but mark the document as removed
        # A complete implementation would rebuild the index, but that's expensive
        
        # Save after removal
        self.save()
        
        logger.info(f"Document {doc_id} removed from vector store")
        return True
    
    def has_document(self, doc_id):
        """
        Check if a document exists in the vector store
        
        Args:
            doc_id: ID of the document to check
            
        Returns:
            bool: True if document exists, False otherwise
        """
        return doc_id in self.documents
    
    def get_all_documents(self):
        """
        Get all documents in the vector store
        
        Returns:
            list: List of document dictionaries with metadata
        """
        documents = []
        for doc_id, doc_info in self.documents.items():
            documents.append({
                'id': doc_id,
                'filename': doc_info.get('filename', doc_id),
                'upload_time': doc_info.get('upload_time'),
                'chunks_count': len(doc_info.get('chunks', []))
            })
        return documents
    
    def get_document(self, doc_id):
        """
        Get a specific document by ID
        
        Args:
            doc_id: ID of the document to retrieve
            
        Returns:
            dict: Document information or None if not found
        """
        if doc_id in self.documents:
            doc_info = self.documents[doc_id]
            return {
                'id': doc_id,
                'filename': doc_info.get('filename', doc_id),
                'upload_time': doc_info.get('upload_time'),
                'text': doc_info.get('text', ''),
                'chunks': doc_info.get('chunks', []),
                'chunks_count': len(doc_info.get('chunks', []))
            }
        return None
    
    def add_document(self, document_id, text_chunks, embeddings, metadata=None):
        """
        Add a document to the vector store (updated signature)
        
        Args:
            document_id: Unique identifier for the document
            text_chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Optional metadata dictionary
        """
        if metadata is None:
            metadata = {}
            
        # Store document info
        self.documents[document_id] = {
            'chunks': text_chunks,
            'chunk_start_idx': len(self.doc_ids),
            'filename': metadata.get('filename', document_id),
            'upload_time': metadata.get('upload_time'),
            'text': ' '.join(text_chunks)  # Join chunks for full text
        }
        
        # Add embeddings to FAISS index
        embeddings_np = np.array(embeddings).astype('float32')
        self.index.add(embeddings_np)
        
        # Track document IDs for each embedding
        for _ in range(len(text_chunks)):
            self.doc_ids.append(document_id)
            
        # Save after adding
        self.save()
        
        logger.info(f"Document {document_id} added with {len(text_chunks)} chunks")
        return document_id
