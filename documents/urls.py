from django.urls import path
from . import views


urlpatterns = [
    path("upload/<int:student_id>/", views.upload_document, name="upload_document_student"),
    path("upload/", views.upload_document, name="upload_document"),
    path("my-documents/", views.my_documents, name="my_documents"),
    path("download/<int:document_id>/", views.download_document, name="download_document"),
    path("preview/<int:document_id>/", views.preview_document, name="preview_document"),
    path("view/<int:document_id>/", views.document_preview, name="document_preview"),
    path("documents/", views.document_list, name="document_list"),
    path("<int:document_id>/", views.document_detail, name="document_detail"),
    path("<int:document_id>/edit/", views.edit_document, name="edit_document"),
]