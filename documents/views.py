from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import DocumentUploadForm
from .services import EncryptionService
from django.http import HttpResponse
from .models import Document


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