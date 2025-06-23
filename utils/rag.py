# Refactor into proper class structure

import os
import logging
import hashlib
import pickle
import numpy as np
import fitz  # PyMuPDF - add this import
from typing import List, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, vector_store, embedding_model=None, llm_model=None):
        """Initialize the RAG system with required components.
        
        Args:
            vector_store: Vector store for document retrieval
            embedding_model: Model for generating embeddings (SentenceTransformer or HuggingFaceEmbeddings)
            llm_model: Language model for response generation
        """
        self.vector_store = vector_store
        
        # Use provided embedding model or create default
        if embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.is_sentence_transformer = True
                logger.info("Using default SentenceTransformer model: all-MiniLM-L6-v2")
            except ImportError:
                logger.warning("sentence-transformers package not found. Please install it or provide embedding_model.")
                self.embedding_model = None
                self.is_sentence_transformer = False
        else:
            self.embedding_model = embedding_model
            # Determine type of embedding model for proper method calling
            self.is_sentence_transformer = hasattr(self.embedding_model, 'encode')
            logger.info(f"Using provided embedding model: {type(self.embedding_model).__name__}")
            
        # Use provided LLM model or re-use existing
        self.llm_model = llm_model
        logger.info("RAG system initialized successfully")
        
    def query(self, question, context=None, k=3, rerank=True):
        """Process a query using the RAG pattern.
        
        Args:
            question: The user question to answer
            context: Optional pre-provided context documents
            k: Number of documents to retrieve
            rerank: Whether to rerank retrieved documents
            
        Returns:
            Generated response based on retrieved/provided context
        """
        try:
            # If context is provided, use it directly
            if context:
                logger.info("Using provided context documents")
                relevant_docs = context
            else:
                logger.info(f"Retrieving {k} documents for query: {question[:50]}...")
                # Generate embedding for the question
                query_embedding = self._get_query_embedding(question)
                
                if query_embedding is None:
                    return "Unable to generate embedding for your question. Please check embedding model configuration."
                
                # Search for relevant documents
                try:
                    relevant_docs = self.vector_store.search(query_embedding, top_k=k)
                    logger.info(f"Retrieved {len(relevant_docs)} documents from vector store")
                except Exception as e:
                    logger.error(f"Vector store search failed: {str(e)}")
                    if hasattr(self.vector_store, 'similarity_search'):
                        logger.info("Falling back to similarity_search method")
                        relevant_docs = self.vector_store.similarity_search(question, k=k)
                    else:
                        raise ValueError("Vector store doesn't support search or similarity_search methods")
                
                if rerank and len(relevant_docs) > 1:
                    logger.info("Reranking documents for better relevance")
                    relevant_docs = self._rerank_documents(question, relevant_docs)
                    
            # Generate response with context
            logger.info("Generating response with context")
            response = self._generate_response(question, relevant_docs)
            
            return response
        except Exception as e:
            error_msg = f"RAG query failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"Sorry, I encountered an error: {str(e)}"
            
    def _get_query_embedding(self, text):
        """Generate embedding for query text using the appropriate method.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector or None if generation fails
        """
        try:
            if not self.embedding_model:
                logger.warning("No embedding model available")
                return None
                
            if self.is_sentence_transformer:
                return self.embedding_model.encode(text)
            else:
                # For HuggingFaceEmbeddings or similar interfaces
                if hasattr(self.embedding_model, 'embed_query'):
                    return self.embedding_model.embed_query(text)
                elif hasattr(self.embedding_model, 'embed_documents'):
                    return self.embedding_model.embed_documents([text])[0]
                else:
                    logger.error("Embedding model has no supported embedding method")
                    return None
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            return None
            
    def _rerank_documents(self, question, documents):
        """Re-rank retrieved documents for better relevance.
        
        Args:
            question: Original query
            documents: List of retrieved documents
            
        Returns:
            Reranked list of documents
        """
        try:
            # First check if documents have score metadata already
            if documents and hasattr(documents[0], 'metadata') and 'score' in documents[0].metadata:
                logger.info("Using existing scores for reranking")
                return sorted(documents, key=lambda x: x.metadata.get('score', 0), reverse=True)
            
            # Simple re-ranking based on semantic similarity
            if not self.embedding_model:
                logger.warning("No embedding model available for reranking, returning original order")
                return documents
                
            # Generate embedding for the question
            question_embedding = self._get_query_embedding(question)
            if question_embedding is None:
                logger.warning("Failed to generate question embedding for reranking")
                return documents
                
            # Calculate similarity scores
            scored_docs = []
            
            for doc in documents:
                # Get document text
                doc_text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                
                # Calculate embedding and similarity
                try:
                    # Get document embedding using appropriate method
                    if self.is_sentence_transformer:
                        doc_embedding = self.embedding_model.encode(doc_text)
                    else:
                        if hasattr(self.embedding_model, 'embed_documents'):
                            doc_embedding = self.embedding_model.embed_documents([doc_text])[0]
                        else:
                            logger.warning("Embedding model doesn't support document embedding")
                            return documents
                    
                    # Calculate cosine similarity
                    similarity = np.dot(question_embedding, doc_embedding) / (
                        np.linalg.norm(question_embedding) * np.linalg.norm(doc_embedding)
                    )
                    
                    # Save score to document metadata for future reference
                    if hasattr(doc, 'metadata'):
                        doc.metadata['score'] = float(similarity)
                        
                    scored_docs.append((doc, similarity))
                except Exception as e:
                    logger.error(f"Error calculating similarity for document: {str(e)}")
                    scored_docs.append((doc, 0.0))
            
            # Sort by score in descending order
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Return just the documents
            return [doc for doc, score in scored_docs]
        except Exception as e:
            logger.error(f"Error during document re-ranking: {str(e)}")
            # Fall back to original documents if re-ranking fails
            return documents
            
    def _generate_response(self, question, context):
        """Generate response using the LLM with context.
        
        Args:
            question: User question
            context: Retrieved documents providing context
            
        Returns:
            Generated response text
        """
        try:
            if not self.llm_model:
                return "No language model available to generate a response."
            
            # Prepare prompt with context
            context_text = ""
            
            # Extract and limit context to prevent token overflow
            for i, doc in enumerate(context[:5]):  # Limit to 5 documents
                if hasattr(doc, 'page_content'):
                    doc_text = doc.page_content
                    source = f" (Source: {doc.metadata.get('source', 'unknown')}" if hasattr(doc, 'metadata') else ""
                    if hasattr(doc, 'metadata') and 'page' in doc.metadata:
                        source += f", Page: {doc.metadata['page'] + 1})"
                    else:
                        source += ")"
                else:
                    doc_text = str(doc)
                    source = ""
                
                # Add to context with numbering and source info
                context_text += f"[{i+1}]{source}\n{doc_text.strip()}\n\n"
              # Create a well-formatted prompt that includes the context and question
            prompt = f"""
You are a knowledgeable AI assistant specializing in providing clear, well-structured answers. 
Please answer the user's question based on the provided context information.

INSTRUCTIONS:
- Provide a comprehensive, well-organized response
- Use bullet points, numbered lists, or sections when appropriate
- Include relevant examples or details from the context
- If the context doesn't contain enough information, clearly state what you know and what you cannot determine
- Format your response to be easy to read and understand

CONTEXT INFORMATION:
{context_text.strip()}

USER QUESTION: {question}

RESPONSE:
"""
            
            # Generate response using the LLM
            try:
                # Handle different LLM interfaces
                if hasattr(self.llm_model, 'generate'):
                    response = self.llm_model.generate([prompt])
                elif hasattr(self.llm_model, 'predict'):
                    response = self.llm_model.predict(prompt)
                elif hasattr(self.llm_model, '__call__'):
                    response = self.llm_model(prompt)
                else:
                    logger.error("LLM model has no supported generation method")
                    return "Error: Language model doesn't support a recognized generation method."
                
                # Cleanup response if needed
                if isinstance(response, dict):
                    if 'text' in response:
                        response = response['text']
                    elif 'generated_text' in response:
                        response = response['generated_text']
                    elif 'response' in response:
                        response = response['response']
                    else:
                        response = str(response)
                elif isinstance(response, list) and len(response) > 0:
                    if isinstance(response[0], dict) and 'text' in response[0]:
                        response = response[0]['text']
                    else:
                        response = str(response[0])
                
                # Format the response for better readability
                response = self._format_response(response)
                
                return response
            except Exception as e:
                logger.error(f"Error in LLM generation: {str(e)}")
                return f"I encountered an error while generating a response: {str(e)}"
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error while generating a response: {str(e)}"
    
    def _format_response(self, response_text):
        """Format the response text for better readability"""
        if not response_text or not isinstance(response_text, str):
            return response_text
        
        # Clean up the response
        formatted_response = response_text.strip()
        
        # Remove any duplicate prompts or unwanted text
        lines = formatted_response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines at the beginning
            if not line and not cleaned_lines:
                continue
            # Skip lines that look like prompts or instructions
            if line.startswith(('You are', 'INSTRUCTIONS:', 'CONTEXT INFORMATION:', 'USER QUESTION:', 'RESPONSE:')):
                continue
            cleaned_lines.append(line)
        
        # Rejoin lines and format
        formatted_response = '\n'.join(cleaned_lines).strip()
        
        # Add some basic formatting improvements
        # Convert numbered lists to proper format
        import re
        formatted_response = re.sub(r'^(\d+)\.\s*', r'\n\1. ', formatted_response, flags=re.MULTILINE)
        
        # Ensure proper spacing around bullet points
        formatted_response = re.sub(r'^[\*\-]\s*', r'\n• ', formatted_response, flags=re.MULTILINE)
        
        # Clean up extra newlines
        formatted_response = re.sub(r'\n{3,}', '\n\n', formatted_response)
        
        return formatted_response.strip()
    
    def summarize_document(self, doc_id):
        """Generate a summary for a specific document"""
        try:
            # Get the document from vector store
            document = self.vector_store.get_document(doc_id)
            if not document:
                logger.error(f"Document {doc_id} not found in vector store")
                return "Document not found."
            
            # Get the full text of the document
            full_text = document.get('text', '')
            if not full_text:
                # If no full text, try to reconstruct from chunks
                chunks = document.get('chunks', [])
                if chunks:
                    full_text = ' '.join(chunks)
                else:
                    return "No content found in document."
            
            # Create a summarization prompt
            filename = document.get('filename', doc_id)
            prompt = f"""
Please provide a comprehensive summary of the following document titled "{filename}":

Document Content:
{full_text[:4000]}  

Provide a clear, structured summary that includes:
1. Main topics covered
2. Key concepts and definitions
3. Important points and conclusions
4. Overall purpose or objective of the document

Summary:
"""
            
            # Generate summary using the LLM
            try:
                if hasattr(self.llm_model, 'invoke'):
                    response = self.llm_model.invoke(prompt)
                elif hasattr(self.llm_model, 'generate'):
                    response = self.llm_model.generate([prompt])
                elif hasattr(self.llm_model, 'predict'):
                    response = self.llm_model.predict(prompt)
                elif hasattr(self.llm_model, '__call__'):
                    response = self.llm_model(prompt)
                else:
                    logger.error("LLM model has no supported generation method")
                    return self._fallback_summary(document)
                
                # Cleanup response if needed
                if isinstance(response, dict):
                    if 'text' in response:
                        response = response['text']
                    elif 'generated_text' in response:
                        response = response['generated_text']
                    elif 'response' in response:
                        response = response['response']
                    else:
                        response = str(response)
                elif isinstance(response, list) and len(response) > 0:
                    if isinstance(response[0], dict) and 'text' in response[0]:
                        response = response[0]['text']
                    else:
                        response = str(response[0])
                
                # Format the response
                formatted_response = self._format_response(response)
                return formatted_response
                
            except Exception as e:
                logger.error(f"Error in LLM generation for summary: {str(e)}")
                return self._fallback_summary(document)
                
        except Exception as e:
            logger.error(f"Error summarizing document {doc_id}: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def _fallback_summary(self, document):
        """Generate a fallback summary when LLM is unavailable"""
        filename = document.get('filename', 'Unknown')
        chunks_count = len(document.get('chunks', []))
        
        return f"""Document Summary

Filename: {filename}
Content Structure: {chunks_count} text sections

This document contains structured content that has been processed and stored in the system. 
To get a detailed AI-generated summary, please ensure your language model is properly configured.

Key Information:
• Document has been successfully processed
• Content is searchable through the query system
• You can ask specific questions about the document content

For detailed analysis, try asking specific questions about the document content."""

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_pdf(self, pdf_path: str, max_workers: int = 4) -> List[Document]:
        import fitz  # PyMuPDF
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return []
        doc_id = os.path.basename(pdf_path)
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        if total_pages <= 10:
            return self._process_pdf_sequential(pdf_document, doc_id, pdf_path)
        return self._process_pdf_multithreaded(pdf_document, doc_id, pdf_path, max_workers)

    def _process_pdf_sequential(self, pdf_document, doc_id: str, pdf_path: str) -> List[Document]:
        documents = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            if not text.strip():
                continue
            documents.extend(self._chunk_text(text, page_num, doc_id, pdf_path))
        return documents

    def _process_pdf_multithreaded(self, pdf_document, doc_id: str, pdf_path: str, max_workers: int) -> List[Document]:
        total_pages = len(pdf_document)
        documents = []
        pages_per_worker = max(1, total_pages // max_workers)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(0, total_pages, pages_per_worker):
                start_page = i
                end_page = min(i + pages_per_worker, total_pages)
                futures.append(executor.submit(
                    self._process_page_range, pdf_document, start_page, end_page, doc_id, pdf_path
                ))
            for future in futures:
                documents.extend(future.result())
        return documents

    def _process_page_range(self, pdf_document, start_page: int, end_page: int, doc_id: str, pdf_path: str) -> List[Document]:
        page_documents = []
        for page_num in range(start_page, end_page):
            page = pdf_document[page_num]
            text = page.get_text()
            if not text.strip():
                continue
            page_documents.extend(self._chunk_text(text, page_num, doc_id, pdf_path))
        return page_documents

    def _chunk_text(self, text: str, page_num: int, doc_id: str, pdf_path: str) -> List[Document]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            if not chunk_text.strip():
                continue
            chunk_id = f"{doc_id}_p{page_num}_c{i//self.chunk_size}"
            metadata = {
                "source": pdf_path,
                "page": page_num,
                "chunk": i // self.chunk_size,
                "id": chunk_id,
                "document_id": doc_id
            }
            doc = Document(page_content=chunk_text, metadata=metadata)
            chunks.append(doc)
        return chunks

class EmbeddingManager:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", cache_dir: str = "cache/embeddings"):
        self.model_name = model_name
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name, cache_folder=cache_dir)
        self._cache = {}
        self._load_cache()

    def _load_cache(self) -> None:
        cache_file = os.path.join(self.cache_dir, "embedding_cache.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    self._cache = pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading embedding cache: {str(e)}")
                self._cache = {}

    def _save_cache(self) -> None:
        if not self._cache:
            return
        cache_file = os.path.join(self.cache_dir, "embedding_cache.pkl")
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(self._cache, f)
        except Exception as e:
            logger.error(f"Error saving embedding cache: {str(e)}")

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def generate_embeddings(self, texts: Union[str, List[str]], use_cache: bool = True) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        if not texts:
            logger.warning("Empty text list provided to generate_embeddings")
            return []
        
        # Clean text entries
        cleaned_texts = [str(text).strip() if text is not None else " " for text in texts]
        
        # Create result array with same size as input
        embeddings = [None] * len(cleaned_texts)
        uncached_texts = []
        uncached_indices = []
        
        # Get cached embeddings
        if use_cache:
            for i, text in enumerate(cleaned_texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    embeddings[i] = self._cache[cache_key]
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = cleaned_texts
            uncached_indices = list(range(len(cleaned_texts)))
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                batch_embeddings = self.embedding_model.embed_documents(uncached_texts)
                
                # Update cache and results
                for idx, embedding in zip(uncached_indices, batch_embeddings):
                    if use_cache:
                        cache_key = self._get_cache_key(cleaned_texts[idx])
                        self._cache[cache_key] = embedding
                    embeddings[idx] = embedding
                    
                if use_cache:
                    self._save_cache()
            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                dim = 384  # Default dimension
                for idx in uncached_indices:
                    embeddings[idx] = [0.0] * dim
    
        # Ensure no None values remain
        return [emb if emb is not None else [0.0] * 384 for emb in embeddings]

def format_response(query, context_results, ai_response):
    formatted_response = {
        "query": query,
        "answer": ai_response,
        "sources": []
    }
    
    # Process each source document
    for i, result in enumerate(context_results):
        source = {
            "title": result.metadata.get("title", f"Source {i+1}"),
            "url": result.metadata.get("source", ""),
            "content_snippet": result.page_content[:150] + "...",
            "relevance": result.metadata.get("score", "")
        }
        formatted_response["sources"].append(source)
    
    return formatted_response


