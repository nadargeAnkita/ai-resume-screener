"""
utils.py  –  File extraction helpers for PDF and DOCX resumes.
"""


def extract_text_from_pdf(file) -> str:
    """Extract all text from an uploaded PDF file object."""
    text = ""
    file_bytes = file.read()

    # Method 1: pdfplumber (best for text-based PDFs)
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            text = "\n".join(pages_text)
        if text.strip():
            return text
    except Exception:
        pass

    # Method 2: PyPDF2 fallback
    try:
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        text = "\n".join(pages_text)
        if text.strip():
            return text
    except Exception:
        pass

    # Method 3: PyMuPDF fallback
    try:
        import fitz
        import io
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = [page.get_text() for page in doc]
        text = "\n".join(pages_text)
        if text.strip():
            return text
    except Exception:
        pass

    return text


def extract_text_from_docx(file) -> str:
    """Extract all text from an uploaded DOCX file object."""
    try:
        import docx
        doc = docx.Document(file)
        paragraphs = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[Error reading DOCX: {e}]"