"""
PDF Assistant Application Entry Point
"""
import os
from app import create_app

# Create Flask application using factory pattern
app = create_app()

if __name__ == "__main__":
    # Get configuration from environment
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    
    print(f"Starting PDF Assistant on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug_mode)