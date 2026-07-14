from django.db import models
from users.models import CustomUser
from student.models import Student

class Document(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="uploaded_documents")
    title =  models.CharField(max_length=255)
    original_file = models.FileField(upload_to="documents/original/")
    encrypted_file = models.FileField(upload_to="documents/encrypted/", null=True, blank=True)
    encrypted_key = models.BinaryField(null=True, blank=True)
    class Status(models.TextChoices):
        PENDING =  "PENDING", "Pending"
        ENCRYPTED = "ENCRYPTED", "Encrypted"

    status =  models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    encrypted_at =  models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    