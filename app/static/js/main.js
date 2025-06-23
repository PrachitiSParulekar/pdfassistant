/**
 * PDF Assistant - Main JavaScript
 * Clean and optimized client-side functionality
 */

'use strict';

// Utility functions
const Utils = {
    /**
     * Show notification to user
     * @param {string} message - Message to display
     * @param {string} type - Type of notification (success, error, info, warning)
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            fontFamily: 'inherit',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        });
        
        // Set background color based on type
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'info': '#17a2b8',
            'warning': '#ffc107'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
        });
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 5000);
    },

    /**
     * Format file size in human readable format
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Debounce function to limit rapid calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// File Upload Handler
class FileUploadHandler {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadForm = document.getElementById('uploadForm');
        this.uploadStatus = document.getElementById('uploadStatus');
        
        this.init();
    }

    init() {
        if (!this.uploadArea || !this.fileInput) return;
        
        this.setupDragAndDrop();
        this.setupEventListeners();
    }

    setupDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.preventDefaults.bind(this), false);
            document.body.addEventListener(eventName, this.preventDefaults.bind(this), false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.highlight.bind(this), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.unhighlight.bind(this), false);
        });

        // Handle dropped files
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this), false);
        
        // Handle click to select file
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
    }

    setupEventListeners() {
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', this.handleUpload.bind(this));
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight() {
        this.uploadArea.classList.add('highlight');
    }

    unhighlight() {
        this.uploadArea.classList.remove('highlight');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            this.fileInput.files = files;
            this.handleFileSelect();
        }
    }

    handleFileSelect() {
        const uploadText = this.uploadArea.querySelector('.upload-text p');
        
        if (this.fileInput.files.length > 0) {
            const file = this.fileInput.files[0];
            
            // Validate file type
            if (!file.type.includes('pdf')) {
                Utils.showNotification('Please select a PDF file only', 'error');
                this.fileInput.value = '';
                return;
            }
            
            // Validate file size (16MB limit)
            if (file.size > 16 * 1024 * 1024) {
                Utils.showNotification('File size must be less than 16MB', 'error');
                this.fileInput.value = '';
                return;
            }
            
            uploadText.textContent = `Selected: ${file.name} (${Utils.formatFileSize(file.size)})`;
            uploadText.style.color = '#28a745';
        }
    }

    async handleUpload(e) {
        e.preventDefault();
        
        if (!this.fileInput.files[0]) {
            Utils.showNotification('Please select a file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.fileInput.files[0]);
        
        this.setUploadStatus('Uploading and processing...', 'info');
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.setUploadStatus(`Error: ${data.error}`, 'error');
                Utils.showNotification(`Upload failed: ${data.error}`, 'error');
            } else {
                this.setUploadStatus(`✅ ${data.message}`, 'success');
                Utils.showNotification('PDF uploaded successfully!', 'success');
                
                // Reset form and refresh documents
                this.fileInput.value = '';
                this.uploadArea.querySelector('.upload-text p').textContent = 'Click to select PDF file or drag and drop';
                this.uploadArea.querySelector('.upload-text p').style.color = '';
                
                // Refresh document list if available
                if (window.documentManager) {
                    window.documentManager.loadDocuments();
                }
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.setUploadStatus(`Error: ${error.message}`, 'error');
            Utils.showNotification('Upload failed. Please try again.', 'error');
        }
    }

    setUploadStatus(message, type) {
        if (this.uploadStatus) {
            this.uploadStatus.innerHTML = `<p class="${type}">${message}</p>`;
        }
    }
}

// Query Handler
class QueryHandler {
    constructor() {
        this.queryInput = document.getElementById('queryInput');
        this.queryBtn = document.getElementById('queryBtn');
        this.webSearchOption = document.getElementById('webSearchOption');
        this.queryResponse = document.getElementById('queryResponse');
        
        this.init();
    }

    init() {
        if (!this.queryInput || !this.queryBtn) return;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.queryBtn.addEventListener('click', this.handleQuery.bind(this));
        
        // Submit on Ctrl+Enter
        this.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.handleQuery();
            }
        });
    }

    async handleQuery() {
        const query = this.queryInput.value.trim();
        
        if (!query) {
            this.setResponse('Please enter a question', 'error');
            return;
        }

        const useWebSearch = this.webSearchOption ? this.webSearchOption.checked : false;
        
        this.setResponse('Processing your question...', 'info');
        this.queryBtn.disabled = true;
        this.queryBtn.textContent = 'Processing...';

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    use_web_search: useWebSearch
                })
            });

            const data = await response.json();

            if (data.error) {
                this.setResponse(`Error: ${data.error}`, 'error');
                Utils.showNotification(`Query failed: ${data.error}`, 'error');
            } else {
                this.displayResponse(data);
                Utils.showNotification('Query completed successfully!', 'success');
            }
        } catch (error) {
            console.error('Query error:', error);
            this.setResponse(`Error: ${error.message}`, 'error');
            Utils.showNotification('Query failed. Please try again.', 'error');
        } finally {
            this.queryBtn.disabled = false;
            this.queryBtn.textContent = 'Ask Question';
        }
    }

    displayResponse(data) {
        const responseHtml = `
            <div class="response">
                <h3>Response:</h3>
                <div class="response-text">${this.formatResponse(data.response)}</div>
                <div class="query-info">
                    <small><strong>Query:</strong> ${data.query}</small>
                    <small><strong>Time:</strong> ${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
        `;
        this.queryResponse.innerHTML = responseHtml;
    }

    /**
     * Format markdown-style text for better display
     * @param {string} text - Text to format
     * @returns {string} Formatted HTML
     */
    formatResponse(text) {
        if (!text || typeof text !== 'string') return text;
        
        let formatted = text;
        
        // Convert headers
        formatted = formatted.replace(/^# (.+$)/gm, '<h1>$1</h1>');
        formatted = formatted.replace(/^## (.+$)/gm, '<h2>$1</h2>');
        formatted = formatted.replace(/^### (.+$)/gm, '<h3>$1</h3>');
        
        // Convert bold text
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Convert italic text
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Convert bullet points
        formatted = formatted.replace(/^• (.+$)/gm, '<li>$1</li>');
        
        // Convert numbered lists
        formatted = formatted.replace(/^(\d+)\. (.+$)/gm, '<li>$2</li>');
        
        // Wrap consecutive <li> elements in <ul>
        formatted = formatted.replace(/(<li>.*<\/li>)/gs, function(match) {
            return '<ul>' + match + '</ul>';
        });
        
        // Convert horizontal rules
        formatted = formatted.replace(/^---+$/gm, '<hr>');
        
        // Convert line breaks to paragraphs
        formatted = formatted.replace(/\n\n/g, '</p><p>');
        formatted = '<p>' + formatted + '</p>';
        
        // Clean up empty paragraphs
        formatted = formatted.replace(/<p><\/p>/g, '');
        formatted = formatted.replace(/<p>\s*<\/p>/g, '');
        
        return formatted;
    }

    setResponse(message, type) {
        if (this.queryResponse) {
            this.queryResponse.innerHTML = `<p class="${type}">${message}</p>`;
        }
    }
}

// Document Manager
class DocumentManager {
    constructor() {
        this.documentsList = document.getElementById('documentsList');
        this.init();
    }

    init() {
        if (this.documentsList) {
            this.loadDocuments();
            // Make it globally available
            window.documentManager = this;
        }
    }

    async loadDocuments() {
        if (!this.documentsList) return;
        
        try {
            const response = await fetch('/documents');
            const data = await response.json();

            if (data.documents && data.documents.length > 0) {
                this.displayDocuments(data.documents);
            } else {
                this.documentsList.innerHTML = '<p>No documents uploaded yet.</p>';
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            this.documentsList.innerHTML = '<p class="error">Error loading documents</p>';
        }
    }

    displayDocuments(documents) {
        const documentsHtml = documents.map(doc => `
            <div class="document-item">
                <div class="doc-info">
                    <span class="doc-name">${doc.filename || doc.id}</span>
                    <small class="doc-date">${doc.upload_time ? new Date(doc.upload_time * 1000).toLocaleString() : 'Unknown'}</small>
                </div>
                <div class="doc-actions">
                    <button onclick="documentManager.summarizeDocument('${doc.id}')" class="summarize-btn">Summarize</button>
                    <button onclick="documentManager.deleteDocument('${doc.id}')" class="delete-btn">Delete</button>
                </div>
            </div>
        `).join('');
        
        this.documentsList.innerHTML = documentsHtml;
    }

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`/document/${docId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.error) {
                Utils.showNotification(`Error: ${data.error}`, 'error');
            } else {
                Utils.showNotification('Document deleted successfully', 'success');
                this.loadDocuments(); // Refresh list
            }
        } catch (error) {
            console.error('Delete error:', error);
            Utils.showNotification('Failed to delete document', 'error');        }
    }

    async summarizeDocument(docId) {
        try {
            Utils.showNotification('Generating summary...', 'info');
            
            const response = await fetch(`/summarize/${docId}`);
            const data = await response.json();
            
            if (data.error) {
                Utils.showNotification(`Error: ${data.error}`, 'error');
            } else {
                // Display summary in dedicated summary section
                const summarySection = document.getElementById('summarySection');
                const documentSummary = document.getElementById('documentSummary');
                
                if (summarySection && documentSummary) {
                    // Show the summary section with animation
                    summarySection.style.display = 'block';
                    
                    // Use the same formatting function as query responses
                    const formattedSummary = window.queryHandler ? 
                        window.queryHandler.formatResponse(data.summary) : 
                        data.summary;
                    
                    documentSummary.innerHTML = `
                        <div class="response">
                            <h3>📄 Document Summary</h3>
                            <div class="response-text">${formattedSummary}</div>
                            <div class="query-info">
                                <small><strong>Document:</strong> ${data.document_id}</small>
                                <small><strong>Generated:</strong> ${new Date().toLocaleString()}</small>
                            </div>
                        </div>
                    `;
                    
                    // Scroll to the summary section smoothly
                    setTimeout(() => {
                        summarySection.scrollIntoView({ 
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }, 100);
                    
                    // Add visual highlight effect
                    summarySection.style.transform = 'scale(1.02)';
                    summarySection.style.transition = 'transform 0.3s ease';
                    setTimeout(() => {
                        summarySection.style.transform = 'scale(1)';
                    }, 300);
                }
                Utils.showNotification('✅ Summary generated successfully!', 'success');
            }
        } catch (error) {
            console.error('Summarize error:', error);
            Utils.showNotification('❌ Failed to generate summary', 'error');
        }
    }
}

// Application Initialization
class PDFAssistant {
    constructor() {
        this.fileUploadHandler = null;
        this.queryHandler = null;
        this.documentManager = null;
        
        this.init();
    }

    init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }

    initializeComponents() {
        try {
            // Initialize components
            this.fileUploadHandler = new FileUploadHandler();
            this.queryHandler = new QueryHandler();
            this.documentManager = new DocumentManager();
            
            // Add dynamic styles
            this.addDynamicStyles();
            
            console.log('🎉 PDF Assistant initialized successfully');
            Utils.showNotification('PDF Assistant ready!', 'success');
            
        } catch (error) {
            console.error('Initialization error:', error);
            Utils.showNotification('Failed to initialize application', 'error');
        }
    }

    addDynamicStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .upload-area.highlight {
                border-color: #764ba2 !important;
                background: rgba(118, 75, 162, 0.1) !important;
                transform: scale(1.02);
                transition: all 0.3s ease;
            }
            
            .doc-info {
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            
            .doc-date {
                color: #666;
                font-size: 0.85rem;
            }
            
            .doc-actions {
                display: flex;
                gap: 0.5rem;
            }
            
            .summarize-btn {
                background: #17a2b8;
                font-size: 0.85rem;
                padding: 0.4rem 0.8rem;
            }
            
            .summarize-btn:hover {
                background: #138496;
            }
            
            .query-info {
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid #eee;
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            
            .response-text {
                line-height: 1.6;
                white-space: pre-wrap;
            }
            
            .response-text ul {
                margin: 0.5rem 0;
                padding-left: 1.5rem;
            }
            
            .response-text li {
                margin: 0.25rem 0;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize the application
new PDFAssistant();