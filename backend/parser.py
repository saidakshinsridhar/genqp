from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader
import pypdfium2
import re
import pytesseract
from pdf2image import convert_from_path
import os


def extract_pdf_text(path):
    # 1. Try pdfminer
    try:
        text = extract_text(path)
        if text and len(text.strip()) > 500:
            return text
    except:
        pass

    # 2. Try PyPDF2
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text and len(text.strip()) > 500:
            return text
    except:
        pass

    # 3. Try pdfium (VERY IMPORTANT)
    try:
        pdf = pypdfium2.PdfDocument(path)
        text = ""
        for page in pdf:
            text += page.get_textpage().get_text_range() + "\n"
        if text and len(text.strip()) > 500:
            return text
    except:
        pass
        # 4. OCR fallback (for image-based PDFs)
    try:
        ocr_text = ocr_extract_pdf(path)
        if ocr_text and len(ocr_text.strip()) > 500:
            return ocr_text
    except Exception:
        pass


    # If everything fails
    raise ValueError(
        "Could not extract readable text from PDF. "
        "PDF may be scanned or heavily formatted."
    )

def preprocess_text(text):
    """
    Cleans raw extracted PDF text for reliable question detection.
    """

    # Normalize newlines
    text = text.replace('\r', '\n')

    # Remove repeated headers / footers (very common)
    text = re.sub(r'CONTINUOUS ASSESSMENT TEST.*?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Regulations.*?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Department of.*?\n', '', text, flags=re.IGNORECASE)

    # Remove COs and Bloom taxonomy junk
    text = re.sub(r'CO\d+[:\s].*?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bK\d\b', '', text)

    # Remove table-like multiple spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Merge broken lines (line wrap fixes)
    text = re.sub(r'\n(?=[a-z])', ' ', text)

    # Reduce excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()
def ocr_extract_pdf(path):
    """
    OCR fallback for image-based PDFs (Part B / Part C diagrams).
    """
    images = convert_from_path(path, dpi=300)
    text = ""

    for img in images:
        text += pytesseract.image_to_string(img) + "\n"

    return text
def extract_images_from_pdf(pdf_path, output_dir="assets/diagrams"):
    """
    Extracts images (diagrams) from PDF and saves them as PNG files.
    Returns list of saved image paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    images = convert_from_path(pdf_path, dpi=300)
    saved = []

    for i, img in enumerate(images):
        path = os.path.join(output_dir, f"page_{i+1}.png")
        img.save(path, "PNG")
        saved.append(path)

    return saved
