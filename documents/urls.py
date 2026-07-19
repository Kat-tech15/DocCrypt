from django.urls import path
from .views import (
    download_document,
    my_documents,
    upload_document,
)


urlpatterns = [
    path("upload/", upload_document, name="upload_document"),
    path("my-documents/", my_documents, name="my_documents"),
    path("download/<int:document_id>/", download_document, name="download_document"),
]