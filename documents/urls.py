from django.urls import path
from . import views


urlpatterns = [
    path("upload/", views.upload_document, name="upload_document"),
    path("my-documents/", views.my_documents, name="my_documents"),
    path("download/<int:document_id>/", views.download_document, name="download_document"),
    path("documents/", views.document_list, name="document_list"),
    path("<int:document>/", views.document_detail, name="document_detail"),
    path("<int:document_id>/edit/", views.edit_document, name="edit_document"),
]