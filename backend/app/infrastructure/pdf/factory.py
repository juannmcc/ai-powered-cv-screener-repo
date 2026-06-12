from app.domain.ports.pdf_port import PDFPort
from app.infrastructure.pdf.pdfplumber_adapter import PDFPlumberAdapter


def get_pdf_reader() -> PDFPort:
    return PDFPlumberAdapter()
