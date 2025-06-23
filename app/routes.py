"""
PDF Assistant Routes
"""
import os
import sys
import time
import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from typing import Dict, List, Any
import hashlib

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_parser import extract_text_from_pdf
from utils.embeddings import generate_embeddings

# Create blueprint
main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_content: bytes) -> str:
    """Generate hash for file content"""
    return hashlib.md5(file_content).hexdigest()

@main.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Read file content
        file_content = file.read()
        file_hash = get_file_hash(file_content)
        
        # Check if file already processed
        if current_app.vector_store.has_document(file_hash):
            return jsonify({
                "message": "File already processed",
                "document_id": file_hash,
                "filename": filename
            })
        
        # Extract text from PDF
        text_chunks = extract_text_from_pdf(file_content)
        if not text_chunks:
            return jsonify({"error": "Could not extract text from PDF"}), 400
        
        # Generate embeddings
        embeddings = generate_embeddings(text_chunks)
        
        # Store in vector database
        doc_id = current_app.vector_store.add_document(
            document_id=file_hash,
            text_chunks=text_chunks,
            embeddings=embeddings,
            metadata={"filename": filename, "upload_time": time.time()}
        )
        
        logger.info(f"Successfully processed document: {filename} (ID: {doc_id})")
        
        return jsonify({
            "message": "File processed successfully",
            "document_id": doc_id,
            "filename": filename,
            "chunks_processed": len(text_chunks)
        })
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({"error": "Failed to process file"}), 500

@main.route('/query', methods=['POST'])
def query_documents():
    """Handle document query requests"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400
        
        use_web_search = data.get('use_web_search', False)
        
        # Process query using RAG system
        response = current_app.rag_system.query(
            question=query
        )
        
        return jsonify({
            "response": response,
            "query": query,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": "Failed to process query"}), 500

@main.route('/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        documents = current_app.vector_store.get_all_documents()
        return jsonify({
            "documents": documents,
            "count": len(documents)
        })
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({"error": "Failed to retrieve documents"}), 500

@main.route('/document/<doc_id>', methods=['DELETE'])
def delete_document(doc_id: str):
    """Delete a specific document"""
    try:
        if current_app.vector_store.remove_document(doc_id):
            return jsonify({"message": "Document deleted successfully"})
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {str(e)}")
        return jsonify({"error": "Failed to delete document"}), 500

@main.route('/summarize/<doc_id>', methods=['GET'])
def summarize_document(doc_id: str):
    """Generate summary for a specific document"""
    try:
        # Get document content
        document = current_app.vector_store.get_document(doc_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Generate summary using RAG system
        summary = current_app.rag_system.summarize_document(doc_id)
        
        return jsonify({
            "document_id": doc_id,
            "summary": summary,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error summarizing document {doc_id}: {str(e)}")
        return jsonify({"error": "Failed to generate summary"}), 500

@main.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    })