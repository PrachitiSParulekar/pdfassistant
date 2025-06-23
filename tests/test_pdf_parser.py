import unittest
import os
import tempfile
from utils.pdf_parser import improved_chunking, process_pdf_multithreaded

class TestPDFParser(unittest.TestCase):
    def setUp(self):
        # Create test directory if it doesn't exist
        test_files_dir = os.path.join(os.path.dirname(__file__), 'test_files')
        os.makedirs(test_files_dir, exist_ok=True)
        
        self.test_pdf_path = os.path.join(test_files_dir, 'sample.pdf')
        
        # If test file doesn't exist, create a dummy one
        if not os.path.exists(self.test_pdf_path):
            self._create_dummy_pdf()
            
        self.sample_text = """# Section 1
        
This is the first section with some content.

## Subsection 1.1

More detailed information here.

# Section 2

This is the second major section of the document.
"""

    def _create_dummy_pdf(self):
        # Import necessary for PDF creation
        try:
            import fitz  # PyMuPDF
        except ImportError:
            self.skipTest("PyMuPDF not installed, skipping test")
            
        # Create a simple PDF for testing
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test PDF content", fontsize=12)
        doc.save(self.test_pdf_path)
        doc.close()

    def test_improved_chunking(self):
        chunk_text, chunk_metadata = improved_chunking(self.sample_text, chunk_size=50)
        self.assertGreater(len(chunk_text), 1)
        self.assertIn("Section 1", chunk_text[0])
        self.assertIn("Section 2", chunk_text[-1])
        
        # Test metadata
        self.assertEqual(len(chunk_text), len(chunk_metadata))
        for metadata in chunk_metadata:
            self.assertIn("chunk_id", metadata)

    def test_multithreaded_processing(self):
        if os.path.exists(self.test_pdf_path):
            result = process_pdf_multithreaded(self.test_pdf_path)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        else:
            self.skipTest("Test PDF file not available")
            
    def tearDown(self):
        # Clean up is optional - you might want to keep test files for debugging
        pass