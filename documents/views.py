from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from pathlib import Path
from .forms import DocumentUploadForm
from .services import EncryptionService
from django.http import HttpResponse
from .models import Document
import mimetypes
from .pdf_services import PDFService

@login_required
def upload_document(request):

    if request.method == "POST":

        form = DocumentUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            document = form.save(commit=False)

            document.uploaded_by = request.user

            document.save()

            EncryptionService.encrypt_document(document)

            return render(
                request,
                "documents/upload_success.html",
                {
                    "document": document
                }
            )

    else:

        form = DocumentUploadForm()

    return render(
        request,
        "documents/upload_document.html",
        {
            "form": form
        }
    )

def test_decryption(request):
    document = Document.objects.filter(status=Document.Status.ENCRYPTED).first()

    if not document:
        return HttpResponse("No encrypted documents found.")
    
    original_data = EncryptionService.decrypt_document(document, document.student.admission_number)

    return HttpResponse(f"Decryption successful! File Size: {len(original_data)} bytes")

@login_required
def my_documents(request):
    student = request.user.student
    documents = Document.objects.filter(student=student).order_by("-uploaded_at")

    context = {"documents": documents}

    return render(request, "documents/my_documents.html", context)

@login_required
def download_document(request, document_id):

    document = get_object_or_404(
        Document,
        id=document_id
    )

    if request.user.role == request.user.Role.STUDENT:
        if document.student.user != request.user:
            return HttpResponse(
                "You are not authorized to download this document.",
                status=403
            )

    original_data = EncryptionService.decrypt_document(
        document,
        document.student.admission_number
    )
    password = PDFService.generate_pdf_password(document.student.admission_number)
    
    protected_pdf = PDFService.protect_pdf(original_data, password)
    
    filename = Path(document.original_file.name).name

    response = HttpResponse(
        protected_pdf, content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response

