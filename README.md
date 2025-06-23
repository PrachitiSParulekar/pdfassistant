# 📚 PDF Assistant

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Flask-based web application that provides intelligent PDF processing capabilities using RAG (Retrieval-Augmented Generation) technology. Upload PDFs, ask questions about their content, and get AI-powered responses with document summarization features.

## ✨ Features

- **📄 PDF Upload & Processing**: Upload and process PDF documents with advanced text extraction
- **🤖 AI-Powered Querying**: Ask natural language questions about your PDF content
- **🔍 Vector Search**: Efficient similarity search using FAISS vector database
- **🧠 RAG System**: Advanced retrieval-augmented generation for accurate responses
- **🌐 Web Search Integration**: Optional web search to enhance responses with external knowledge
- **📋 Document Management**: View, list, delete, and summarize uploaded documents
- **📊 Document Summarization**: Generate AI-powered summaries of your documents
- **🔗 Clean API**: RESTful API endpoints for all operations
- **💻 Modern UI**: Responsive web interface with smooth animations
- **🎨 Beautiful Design**: Modern gradient UI with intuitive user experience

## 🎬 Demo

### Quick Start
1. Upload a PDF document using the drag-and-drop interface
2. Ask questions about the document content
3. Generate AI-powered summaries
4. Use web search integration for enhanced responses

### Example Usage
```
📤 Upload: "Upload your research paper, textbook, or any PDF document"
❓ Query: "What are the main conclusions of this paper?"
📋 Summary: "Generate a comprehensive summary of the document"
🔍 Enhanced Search: "Enable web search for broader context"
```

### Screenshots
*Note: Add screenshots of your application interface here*

- Main dashboard with upload interface
- Document management and query interface  
- Summary generation and results display
- Mobile-responsive design

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

## 💡 How It Works

1. **Document Processing**: PDFs are parsed and text is extracted using advanced libraries
2. **Embeddings Generation**: Text content is converted to vector embeddings
3. **Vector Storage**: Embeddings are stored in FAISS for efficient similarity search
4. **Query Processing**: User questions are embedded and matched against document content
5. **RAG Response**: Relevant context is retrieved and used to generate accurate responses
6. **Summarization**: Documents are analyzed to create concise, informative summaries

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

### Environment Variables
Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
FLASK_ENV=development

# AI Service API Keys (choose one or more)
OPENAI_API_KEY=your-openai-api-key          # For GPT models
HUGGINGFACE_API_KEY=your-huggingface-key    # For Hugging Face models
ANTHROPIC_API_KEY=your-anthropic-key        # For Claude models

# Application Settings
MAX_CONTENT_LENGTH=16777216                  # 16MB max file size
UPLOAD_FOLDER=uploads
CACHE_FOLDER=cache
```

### Supported AI Models
- **OpenAI GPT**: GPT-3.5-turbo, GPT-4
- **Hugging Face**: Various open-source models
- **Anthropic Claude**: Claude-3, Claude-2
- **Local Models**: Sentence transformers for embeddings

## 🚀 Deployment

### Using Docker
```bash
# Build the image
docker build -t pdf-assistant .

# Run the container
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads pdf-assistant
```

### Using Heroku
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-openai-key

# Deploy
git push heroku main
```

## 📊 Performance

- **File Size Limit**: 16MB per PDF
- **Supported Formats**: PDF (text-based)
- **Response Time**: 2-5 seconds for queries
- **Concurrent Users**: Scalable with proper deployment
- **Storage**: Local file system (easily configurable for cloud storage)

## 🛠️ Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python test_complete_system.py

# Run with coverage
pip install pytest-cov
python -m pytest --cov=app tests/
```

### Code Structure
```
app/
├── static/js/main.js      # Frontend JavaScript
├── static/css/style.css   # Styling and animations
├── templates/             # HTML templates
└── routes.py             # Flask routes and API endpoints

utils/
├── rag.py                # RAG system implementation  
├── llm.py                # AI model integration
├── pdf_parser.py         # PDF processing
├── vector_store.py       # Vector database operations
└── embeddings.py         # Text embedding generation
```

## 🔍 Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
pip install -r requirements.txt
```

**PDF processing errors**:
- Ensure PDF contains extractable text
- Check file size is under 16MB
- Verify PDF is not password protected

**AI model errors**:
- Verify API keys are correctly set
- Check internet connection for API calls
- Ensure sufficient API quota/credits

**Vector store issues**:
```bash
# Clear cache and restart
rm -rf cache/embeddings/*
python run.py
```

### Getting Help
- Check the [Issues](../../issues) section
- Read the documentation in `WHERE_TO_FIND_SUMMARIES.md`
- Review test files for usage examples
