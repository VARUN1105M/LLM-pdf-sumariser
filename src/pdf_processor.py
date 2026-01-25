import pdfplumber
from pathlib import Path
from typing import List, Tuple

class PDFProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting {pdf_path}: {e}")
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if len(chunk.strip()) > 50:  # Skip tiny chunks
                chunks.append(chunk)
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> Tuple[str, List[str]]:
        """Extract and chunk a PDF"""
        text = self.extract_text(pdf_path)
        chunks = self.chunk_text(text)
        return text, chunks
    
    def process_directory(self, directory: str) -> dict:
        """Process all PDFs in a directory"""
        pdf_dir = Path(directory)
        results = {}
        
        for pdf_file in pdf_dir.glob("*.pdf"):
            print(f"Processing {pdf_file.name}...")
            text, chunks = self.process_pdf(str(pdf_file))
            results[pdf_file.name] = {
                'text': text,
                'chunks': chunks,
                'chunk_count': len(chunks)
            }
        
        return results