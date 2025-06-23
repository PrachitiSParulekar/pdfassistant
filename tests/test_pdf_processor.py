import unittest
from app.utils.pdf_processor import PdfProcessor

class TestPdfProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = PdfProcessor()

    def test_extract_text(self):
        # Test extracting text from a sample PDF
        sample_pdf_path = 'path/to/sample.pdf'
        expected_text = 'Expected text from the sample PDF'
        extracted_text = self.processor.extract_text(sample_pdf_path)
        self.assertEqual(extracted_text, expected_text)

    def test_merge_pdfs(self):
        # Test merging multiple PDFs
        pdf_list = ['path/to/first.pdf', 'path/to/second.pdf']
        output_pdf_path = 'path/to/output.pdf'
        self.processor.merge_pdfs(pdf_list, output_pdf_path)
        # Check if the output PDF exists and is not empty
        self.assertTrue(os.path.exists(output_pdf_path))
        self.assertGreater(os.path.getsize(output_pdf_path), 0)

    def test_split_pdf(self):
        # Test splitting a PDF into individual pages
        sample_pdf_path = 'path/to/sample.pdf'
        output_dir = 'path/to/output/directory'
        self.processor.split_pdf(sample_pdf_path, output_dir)
        # Check if the output directory contains the expected number of pages
        expected_page_count = 5  # Assuming the sample PDF has 5 pages
        actual_page_count = len(os.listdir(output_dir))
        self.assertEqual(actual_page_count, expected_page_count)

if __name__ == '__main__':
    unittest.main()