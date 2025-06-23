"""
PDF Assistant Flask Application Factory
"""
import os
import sys
import logging
from flask import Flask

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from utils.vector_store import VectorStore
from utils.rag import RAGSystem
from utils.llm import get_llm_model
from utils.web_search import WebSearch


def create_app(config_name='development'):
    """Application factory pattern for creating Flask app"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Initialize components
    with app.app_context():
        # Initialize vector store
        app.vector_store = VectorStore()
        
        # Initialize embedding model
        app.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize LLM model
        app.llm_model = get_llm_model()
        
        # Initialize web search
        app.web_search = WebSearch()
        
        # Initialize RAG system
        app.rag_system = RAGSystem(app.vector_store, app.embedding_model, app.llm_model)
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app