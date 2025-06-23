"""Direct server start script"""
import os
import sys

# Ensure we're in the right directory
os.chdir(r"C:\Users\Admin\OneDrive\Documents\Desktop\learning\clg\pdfs\pdf-assistant")

# Add to path
sys.path.insert(0, os.getcwd())

# Import and run
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Starting PDF Assistant on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
