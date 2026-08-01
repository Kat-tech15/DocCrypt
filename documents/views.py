from pathlib import Path
import os
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import DocumentUploadForm, DocumentEditForm
from .models import Document
from .pdf_services import PDFService
from .services import EncryptionService
from django.db.models import Q
from django.core.paginator import Paginator
from student.models import Student
import logging
from notifications.services import NotificationService
from django.urls import reverse

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@login_required
def upload_document(request, student_id=None):
    """
    Upload and encrypt a PDF document.
    """

    if not request.user.is_admin:
        return HttpResponse(
            "Only administrators are allowed to upload documents.",
            status=403,
        )

    # If the upload originated from a student's profile,
    # retrieve that student.
    student = None

    if student_id:
        student = get_object_or_404(Student, id=student_id)

    # Build the form for both GET and POST requests.
    form = DocumentUploadForm(
        request.POST or None,
        request.FILES or None,
        initial={"student": student} if student else None,
    )

    # Prevent changing the student when uploading
    # from the student's profile.
    if student:
        form.fields["student"].disabled = True

    if request.method == "POST" and form.is_valid():

        try:

            with transaction.atomic():

                # Determine which student owns the document.
                selected_student = student or form.cleaned_data["student"]

                # Replace an existing document with the same title.
                existing_document = Document.objects.filter(
                    student=selected_student,
                    title=form.cleaned_data["title"],
                ).first()

                if existing_document:

                    if existing_document.original_file:
                        existing_document.original_file.delete(save=False)

                    if existing_document.encrypted_file:
                        existing_document.encrypted_file.delete(save=False)

                    existing_document.delete()

                # Save the new document.
                document = form.save(commit=False)

                document.student = selected_student
                document.uploaded_by = request.user

                if request.FILES.get("original_file"):
                    document.original_filename = request.FILES["original_file"].name

                document.save()

                # Encrypt the uploaded document.
                EncryptionService.encrypt_document(document)
                NotificationService.document_uploaded(
                    document,
                    request.user
                    )

            messages.success(
                request,
                "Document uploaded and encrypted successfully."
            )

            return redirect(
                "student_detail",
                student_id=selected_student.id,
            )
        
    
        except Exception:

            messages.error(
                request,
                "An unexpected error occurred while uploading the document."
            )

            raise

    return render(
        request,
        "documents/upload_document.html",
        {
            "form": form,
            "student": student,
        },
    )


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
        ).filter(student=student).order_by("-uploaded_at")
    )

    paginator = Paginator(documents, 10)
    page_number = request.GET.get("page")
    documents = paginator.get_page(page_number)

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

        filename = document.original_filename or "document.pdf"

        response = HttpResponse(protected_pdf, content_type="application/pdf")
        response["Content-Disposition"] = (f'attachment; filename="{filename}"')

        NotificationService.document_downloaded(document)

        return response

    except Exception as e:

        logger.exception("Document download failed.")

        messages.error( request, "Unable to download the requested document.")

        return redirect("my_documents")


@require_http_methods(["GET"])
@login_required
@xframe_options_exempt
def preview_document(request, document_id):

    if not request.user.is_admin:
        return HttpResponseForbidden("Only administrators can preview documents.")

    print(f"Requested ID: {document_id}")

    document = get_object_or_404(Document, id=document_id)

    print("Document:", document.title)

    pdf_data = EncryptionService.decrypt_document(
        document,
        document.student.admission_number,
    )
    NotificationService.document_previewed(
        document,
        request.user,
    )

    response = HttpResponse(
        pdf_data,
        content_type="application/pdf"
    )


    response["Content-Disposition"] = 'inline; filename="preview.pdf"'

    return response

@login_required
def document_preview(request, document_id):
    """
    Display the document preview page.
    """

    if not request.user.is_admin:
        return HttpResponseForbidden(
            "Only administrators can preview documents."
        )

    document = get_object_or_404(Document, id=document_id)

    context = {
        "document": document,
        "preview_url": reverse(
            "preview_document",
            args=[document.id],
        ),
    }

    NotificationService.document_previewed(
        document,
        request.user,
    )

    return render(
        request,
        "documents/document_preview.html",
        context,
    )

@login_required
def document_list(request):
    if not request.user.is_admin:
        return HttpResponseForbidden(request, "This page is only accessible to administrators.")

    documents = Document.objects.select_related("student").all().order_by("student__admission_number")

    query = request.GET.get("q", "")

    if query:
        documents = documents.filter(

            Q(title__icontains=query) |
            Q(student__admission_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(status__icontains=query)
        )

    paginator = Paginator(documents, 10)
    page_number = request.GET.get("page")
    documents = paginator.get_page(page_number)

    context = {"documents": documents, "query": query}

    return render(request, "documents/documents_list.html", context)

@login_required
def document_detail(request, document_id):

    document = get_object_or_404(Document, id=document_id)

    context = {
        "document": document,
        "original_filename": document.original_file,        
        "encrypted_filename": (
                    os.path.basename(document.encrypted_file.name)
                    if document.encrypted_file else "-"
                ),
            }

    return render(request, "documents/document_detail.html", context)


@login_required
def edit_document(request, document_id):

    document = get_object_or_404(Document, id=document_id)

    form = DocumentEditForm(
        request.POST or None, 
        request.FILES or None,
        instance=document,
    )


    if request.method == "POST" and form.is_valid():


        form.save()

        NotificationService.document_updated(document)

        messages.info(request, "Document updated successfully.")

        return redirect("document_detail", document_id=document.id)


    return render(request, "documents/edit_document.html", {"form": form, "document": document})