from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader

def extract_pdf_text(path):
    """
    Try extracting text using pdfminer first.
    If pdfminer fails or returns too little text,
    fallback to PyPDF2.
    """

    # First attempt — pdfminer
    try:
        text = extract_text(path)
        if text and len(text.strip()) > 10:
            return text
    except:
        pass

    # Fallback — PyPDF2
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""
