from io import BytesIO
import logging
from pypdf import PdfReader, PdfWriter


logger = logging.getLogger(__name__)


class PDFService:
    """
    Handles PDF password generation and protection.
    
    """

    @staticmethod
    def generate_pdf_password(admission_number):
        """
        Generate a PDF password from a student's admission number.

        Example:
        SB62/PU/41063/22 -> 6322
        """
        parts = admission_number.split("/")

        if len(parts) != 4 or not all(parts):
            raise ValueError("Invalid admission number format.")

        serial = parts[2][-2:]
        year = parts[3]

        return f"{serial}{year}"

    @staticmethod
    def protect_pdf(pdf_bytes, password):
        """
        Password-protect a PDF and return the protected PDF bytes.
        """
        try:
            input_pdf = BytesIO(pdf_bytes)

            reader = PdfReader(input_pdf)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            output_pdf = BytesIO()
            writer.write(output_pdf)

            logger.info("PDF protected successfully.")

            return output_pdf.getvalue()

        except Exception:
            logger.exception("Failed to protect PDF.")
            raise