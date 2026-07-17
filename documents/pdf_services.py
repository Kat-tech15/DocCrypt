from io import BytesIO 
from pypdf import PdfReader, PdfWriter

class PDFService:
    
    @staticmethod
    def generate_pdf_password(admission_number):
        parts = admission_number.split("/")
        if len(parts) != 4:
            raise ValueError("Invalid admission number format.")
        
        serial = parts[2][-2:]
        year = parts[3]
        return serial + year
    
    @staticmethod
    def protect_pdf(pdf_bytes, password):
        input_stream = BytesIO(pdf_bytes)
        reader = PdfReader(input_stream)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_stream = BytesIO()
        writer.write(output_stream)
        return output_stream.getvalue()