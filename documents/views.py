from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import DocumentUploadForm
from .services import EncryptionService


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