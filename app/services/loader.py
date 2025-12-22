from pypdf import PdfReader
from docx import Document

def load_document(file):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        text = []
        for page in reader.pages:
            if page.extract_text():
                text.append(page.extract_text())
        return "\n".join(text)

    elif filename.endswith(".docx"):
        doc = Document(file.file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file type")