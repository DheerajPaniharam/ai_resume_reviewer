import PyPDF2
import docx2txt

def extract_text(file):
    """Extract text from uploaded PDF or DOCX file."""
    text = ""
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    elif filename.endswith(".docx"):
        text = docx2txt.process(file)
    else:
        text = file.read().decode("utf-8", errors="ignore")
    return text
