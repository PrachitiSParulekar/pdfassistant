# PDF Assistant

A modern Flask-based web application that provides intelligent PDF processing capabilities using RAG (Retrieval-Augmented Generation) technology. Upload PDFs, ask questions about their content, and get AI-powered responses.

## 🚀 Features

- **PDF Upload & Processing**: Upload and process PDF documents with text extraction
- **AI-Powered Querying**: Ask natural language questions about your PDF content
- **Vector Search**: Efficient similarity search using FAISS vector database
- **RAG System**: Advanced retrieval-augmented generation for accurate responses
- **Web Search Integration**: Optional web search to enhance responses
- **Document Management**: View, list, and delete uploaded documents
- **Document Summarization**: Generate AI summaries of your documents
- **Clean API**: RESTful API endpoints for all operations
- **Modern UI**: Responsive web interface

## 🏗️ Architecture

```
pdf-assistant/
├── app/                    # Flask application package
│   ├── __init__.py        # Application factory
│   ├── routes.py          # API routes and endpoints
│   ├── static/            # CSS, JS assets
│   └── templates/         # Jinja2 templates
├── utils/                 # Core utilities
│   ├── pdf_parser.py      # PDF text extraction
│   ├── embeddings.py      # Text embedding generation
│   ├── vector_store.py    # FAISS vector database
│   ├── rag.py            # RAG system implementation
│   ├── llm.py            # Language model interface
│   └── web_search.py     # Web search integration
├── cache/                 # Vector embeddings cache
├── uploads/              # Uploaded PDF files
├── tests/                # Test suite
├── config.py             # Application configuration
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pdf-assistant
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your API keys:
   ```env
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-api-key
   HUGGINGFACE_API_KEY=your-huggingface-api-key
   DEBUG=True
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

   The application will be available at `http://127.0.0.1:5000`

## 📚 API Endpoints

### Document Management
- `POST /upload` - Upload and process PDF files
- `GET /documents` - List all uploaded documents
- `DELETE /document/<doc_id>` - Delete specific document

### Querying
- `POST /query` - Ask questions about document content
- `GET /summarize/<doc_id>` - Generate document summary

### Utility
- `GET /health` - Health check endpoint

## 🔧 Configuration

Key configuration options in `config.py`:

```python
# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf'}

# AI/ML settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_STORE_PATH = "cache/vector_store"

# API Keys (set in .env)
OPENAI_API_KEY = "your-key-here"
HUGGINGFACE_API_KEY = "your-key-here"
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🚀 Deployment

### Production Setup

1. Set environment to production:
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ```

2. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Sentence Transformers](https://www.sbert.net/) - Text embeddings
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [LangChain](https://langchain.com/) - LLM framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
   cd pdf-assistant
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables by copying `.env.example` to `.env` and modifying it as needed.

## Usage

To run the application, execute the following command:
```
python run.py
```

Visit `http://127.0.0.1:5000` in your web browser to access the application.

## Testing

To run the tests, ensure your virtual environment is activated and execute:
```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.