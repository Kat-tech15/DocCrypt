from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_document, name="upload_document"),
    path("test-decryption/", views.test_decryption, name="test_decryption"),
    path("my-documents/", views.my_documents, name="my_documents"),
    path("download/<int:document_id>/", views.download_document, name="download_document"),
]