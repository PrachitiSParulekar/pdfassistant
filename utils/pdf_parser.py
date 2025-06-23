import fitz  # PyMuPDF
import re
import os
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import pypdf
import PyPDF2
import io


logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(file_content):
    """Extract text content from PDF file content (bytes)."""
    try:
        text = ""
        # Use BytesIO to create a file-like object from bytes
        file_stream = io.BytesIO(file_content)
        
        try:
            reader = PyPDF2.PdfReader(file_stream)
            
            # Check if the PDF is encrypted
            if reader.is_encrypted:
                logger.error("PDF is encrypted")
                return "ERROR: This PDF is encrypted or password-protected and cannot be processed."
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            if not text.strip():
                logger.warning("No text extracted from PDF")
                return "WARNING: No text could be extracted from this PDF. It may be scanned or contain only images."
                
            return text
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Failed to read PDF, Error: {str(e)}")
            return f"ERROR: Failed to read PDF file. The file may be corrupted or invalid. Details: {str(e)}"
    except Exception as e:
        logger.error(f"Exception processing PDF, Error: {str(e)}")
        return f"ERROR: An unexpected error occurred while processing the PDF. Details: {str(e)}"

def extract_text_from_pdf(file_path):
    """Extract text content from a PDF file."""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            try:
                reader = PyPDF2.PdfReader(file)
                
                # Check if the PDF is encrypted
                if reader.is_encrypted:
                    logger.error(f"PDF is encrypted: {file_path}")
                    return "ERROR: This PDF is encrypted or password-protected and cannot be processed."
                
                # Extract text from each page
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                if not text.strip():
                    logger.warning(f"No text extracted from PDF: {file_path}")
                    return "WARNING: No text could be extracted from this PDF. It may be scanned or contain only images."
                    
                return text
            except PyPDF2.errors.PdfReadError as e:
                logger.error(f"Failed to read PDF: {file_path}, Error: {str(e)}")
                return f"ERROR: Failed to read PDF file. The file may be corrupted or invalid. Details: {str(e)}"
    except Exception as e:
        logger.error(f"Exception processing PDF: {file_path}, Error: {str(e)}")
        return f"ERROR: An unexpected error occurred while processing the PDF. Details: {str(e)}"

def ensure_text_is_string(text):
    """Ensure text is a string, not a list or other type"""
    if isinstance(text, list):
        # Join list items with spaces
        return ' '.join(text)
    elif not isinstance(text, str):
        # Convert other types to string
        return str(text)
    return text

def split_into_chunks(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks with semantic awareness"""
    # Ensure text is a string
    text = ensure_text_is_string(text)
    
    if not text:
        return []
    
    # Split by paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current_chunk = []
    current_length = 0
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size
        if current_length + len(paragraph) > chunk_size:
            # Save the current chunk
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            
            # Handle paragraphs that are too long by themselves
            if len(paragraph) > chunk_size:
                # Split into sentences and create chunks
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                sentence_chunk = []
                sentence_chunk_length = 0
                
                for sentence in sentences:
                    if sentence_chunk_length + len(sentence) > chunk_size and sentence_chunk:
                        chunks.append(' '.join(sentence_chunk))
                        # Keep overlap
                        last_sentences = sentence_chunk[-2:] if len(sentence_chunk) >= 2 else sentence_chunk
                        sentence_chunk = last_sentences
                        sentence_chunk_length = sum(len(s) for s in last_sentences) + len(last_sentences) - 1
                    
                    sentence_chunk.append(sentence)
                    sentence_chunk_length += len(sentence) + 1
                
                if sentence_chunk:
                    chunks.append(' '.join(sentence_chunk))
                
                # Reset for next paragraph
                current_chunk = []
                current_length = 0
            else:
                # Start new chunk with overlap
                if current_chunk and len(current_chunk) > 1:
                    # Keep last paragraph for overlap
                    current_chunk = [current_chunk[-1]]
                    current_length = len(current_chunk[0])
                else:
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(paragraph)
                current_length += len(paragraph)
        else:
            # Add paragraph to current chunk
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 2  # +2 for \n\n separator
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def extract_raw_text(pdf_path):
    # Check if you have code like this:
    # text = [...some list...]
    # text.split()  # This would cause the error
    
    # Fix by ensuring text is a string, not a list:
    text = extract_text_from_pdf(pdf_path)  # Assuming this returns a list of strings
    
    # If it returns a list, join it into a single string before splitting
    if isinstance(text, list):
        text = ' '.join(text)
    
    # Now you can use split() safely
    return text

def clean_extracted_text(text):
    """Clean up extracted PDF text by removing headers, footers, and page numbers."""
    # Define patterns to remove
    patterns_to_remove = [
        r'©.*?(?=\n|$)',                        # Copyright lines
        r'--- Page \d+ ---',                    # Page markers
        r'^.{0,3}$',                            # Very short lines (3 chars or less)
        r'Topperworld.*?(?=\n|$)',              # Specific header
        r'PDF Assistant:.*?(?=\n|$)',           # App header
        r'• in.*?(?=\n|$)',                     # Bullet points with 'in'
    ]
    
    # Apply each pattern
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
    # Remove consecutive empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def improved_chunking(text, chunk_size=1000):
    """Split text into semantically meaningful chunks"""
    # Split by section boundaries first
    sections = re.split(r'(?=\n\s*#+\s+)', text)
    
    chunks = []
    metadata = []  # Add metadata to match expected return format
    
    for section in sections:
        # If section is too large, split further by paragraphs
        if len(section) > chunk_size:
            paragraphs = section.split("\n\n")
            current_chunk = []
            current_length = 0
            
            for para in paragraphs:
                if current_length + len(para) > chunk_size and current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(chunk_text)
                    metadata.append({"source": "section", "length": len(chunk_text)})
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(para)
                current_length += len(para)
                
            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(chunk_text)
                metadata.append({"source": "section", "length": len(chunk_text)})
        else:
            chunks.append(section)
            metadata.append({"source": "section", "length": len(section)})
    
    return chunks, metadata  # Return both chunks and metadata

def process_pdf_multithreaded(pdf_path, max_workers=4):
    """Process large PDF files using multiple threads"""
    # Implementation for multi-threaded PDF processing
    # ...