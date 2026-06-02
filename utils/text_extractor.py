import io
import os
import tempfile

import PyPDF2
import docx2txt

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(file):
    """Extract text from uploaded PDF, DOCX, or TXT file."""
    filename = getattr(file, "filename", "") or ""
    extension = os.path.splitext(filename.lower())[1]
    data = file.read() or b""

    if extension == ".pdf":
        return _extract_pdf(data)
    if extension == ".docx":
        return _extract_docx(data)
    return _extract_plain_text(data)


def _extract_pdf(data):
    text = ""
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def _extract_docx(data):
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        temp_path = tmp.name

    try:
        return docx2txt.process(temp_path) or ""
    finally:
        os.unlink(temp_path)


def _extract_plain_text(data):
    return data.decode("utf-8", errors="ignore")
