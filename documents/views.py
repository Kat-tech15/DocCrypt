from pathlib import Path
import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import DocumentUploadForm
from .models import Document
from .pdf_services import PDFService
from .services import EncryptionService


@require_http_methods(["GET", "POST"])
@login_required
def upload_document(request):
    """
    Upload and encrypt a PDF document.
    """
    if not request.user.is_superuser:
        return HttpResponse("Only Administrators are allowed to upload documents.", status=403)
    
    if request.method == "POST":
        form = DocumentUploadForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    existing_document = Document.objects.filter(
                        student=form.cleaned_data["student"],
                        title=form.cleaned_data["title"],
                    ).first()

                    if existing_document:
                        if existing_document.original_file:
                            existing_document.original_file.delete(save=False)

                        if existing_document.encrypted_file:
                            existing_document.encrypted_file.delete(save=False)
                        
                        existing_document.delete()

                    document = form.save(commit=False)
                    document.uploaded_by = request.user
                    document.save()

                    EncryptionService.encrypt_document(document)

                messages.success(request, "Document uploaded successfully.")
                return redirect("dashboard")

            except Exception as e:
                print("UPLOAD ERROR")
                print(e)
                print(type(e))
                raise
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload_document.html", {"form": form})


@require_http_methods(["GET"])
@login_required
def my_documents(request):
    """
    Display all documents belonging to the logged-in student.
    """

    if not request.user.is_student:
        return HttpResponse("A student account is required to access this page.", status=403)
    
    student = request.user.student

    documents = (
        Document.objects
        .select_related(
            "student","uploaded_by",
        ).filter(student=student)
    )

    return render(request, "documents/my_documents.html", {"documents": documents})


@require_http_methods(["GET"])
@login_required
def download_document(request, document_id):
    """
    Decrypt and return a password-protected PDF.
    """

    document = get_object_or_404(Document, id=document_id,)

    if (
        request.user.role == request.user.Role.STUDENT
        and document.student.user != request.user
    ):
        return HttpResponse(
            "You are not authorized to download this document.",
            status=403,
        )
    
    document_file = document.encrypted_file
    
    if (
        not document.encrypted_file or not os.path.exists(document_file.path)
    ):
        messages.error(request, "The encrypted document could not be found. Please contact the administrator.")
        return redirect("my_documents")
    
    try:
        original_data = EncryptionService.decrypt_document(
            document,
            document.student.admission_number,
        )

        password = PDFService.generate_pdf_password(
            document.student.admission_number
        )

        protected_pdf = PDFService.protect_pdf(
            original_data,
            password,
        )

        filename = Path(document.original_file.name).name
        response = HttpResponse(protected_pdf, content_type="application/pdf")
        response["Content-Disposition"] = (f'attachment; filename="{filename}"')

        return response

    except Exception:
        messages.error(
            request,
            "Unable to download the requested document.",
        )
        return redirect("my_documents")