from django.urls import path
from . import views

urlpatterns = [
    path("logs/", views.audit_logs, name="audit_logs"),
    path("export/csv/", views.export_audit_logs, name="export_audit_logs"),
    path("export/pdf/", views.export_audit_logs_pdf, name="export_audit_logs_pdf"),
]