from backend.parser import extract_pdf_text
from backend.classifier import classify_questions
from backend.validator import validate_bank
from backend.selector import (
    generate_unit_test,
    generate_cat,
    generate_endsem
)

def generate_papers(pdf_path, exam_type):
    text = extract_pdf_text(pdf_path)
    if not text.strip():
        raise ValueError("Could not extract text from PDF")

    parts = classify_questions(text)

    validate_bank(parts, exam_type)

    if exam_type == "UNIT":
        return generate_unit_test(parts)
    elif exam_type == "CAT":
        return generate_cat(parts)
    elif exam_type == "ENDSEM":
        return generate_endsem(parts)
    else:
        raise ValueError("Unknown exam type")
