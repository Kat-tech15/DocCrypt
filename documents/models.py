from django.db import models
from student.models import Student
from users.models import CustomUser


class Document(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ENCRYPTED = "ENCRYPTED", "Encrypted"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="uploaded_documents")
    title = models.CharField( max_length=255)
    original_file = models.FileField(upload_to="documents/original/")
    encrypted_file = models.FileField(upload_to="documents/encrypted/", null=True, blank=True)
    encrypted_key = models.BinaryField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    encrypted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.student.admission_number} - {self.title}"