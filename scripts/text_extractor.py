#text_extractor.py
import os
import pdfplumber
from docx import Document
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_text_from_txt(txt_path):
    text = ""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
            print(f"Error reading txt {txt_path}: {e}")
    return text.strip()

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text.strip()

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text.strip()

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="deu+eng")  # adjust languages as needed
        return text.strip()
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return ""

def extract_text_from_scanned_pdf(pdf_path):
    """Convert PDF pages to images and OCR each page."""
    text = ""
    try:
        pages = convert_from_path(pdf_path)
        for page_num, page in enumerate(pages):
            page_text = pytesseract.image_to_string(page, lang="deu+eng")
            text += page_text + "\n"
    except Exception as e:
        print(f"Error OCRing scanned PDF {pdf_path}: {e}")
    return text.strip()

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        # Try extracting text normally first
        text = extract_text_from_pdf(file_path)
        if len(text.strip()) < 100:  # Heuristic: If too little text, might be scanned PDF
            print("Detected likely scanned PDF. Running OCR...")
            text = extract_text_from_scanned_pdf(file_path)
        return text

    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)

    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return extract_text_from_image(file_path)


    else:
        print(f"Unsupported file format: {ext}")
        return ""

if __name__ == "__main__":
    # Test example files
    files = [
        "example_report.pdf",
        "example_document.docx",
        "scanned_page.png"
    ]
    for f in files:
        print(f"\nExtracting text from {f}...")
        text = extract_text(f)
        print(f"Extracted text preview:\n{text[:500]}")  # Print first 500 chars
