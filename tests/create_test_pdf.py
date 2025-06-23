import fitz  # PyMuPDF
import os

def create_sample_pdf(output_path):
    """Create a simple test PDF file for testing purposes."""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add some text to the page
    text = "# Sample PDF\n\nThis is a sample PDF file created for testing purposes.\n\n## Section 1\n\nThis is section 1 content.\n\n## Section 2\n\nThis is section 2 content."
    
    # Add text to the page
    page.insert_text((50, 50), text, fontsize=12)
    
    # Save the PDF
    doc.save(output_path)
    doc.close()
    
    print(f"Sample PDF created at {output_path}")

if __name__ == "__main__":
    test_files_dir = os.path.join(os.path.dirname(__file__), "test_files")
    os.makedirs(test_files_dir, exist_ok=True)
    
    output_path = os.path.join(test_files_dir, "sample.pdf")
    create_sample_pdf(output_path)