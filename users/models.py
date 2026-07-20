from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    """
    Custom user model supporting role-based access
    and mandatory password changes.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    must_change_password = models.BooleanField(default=True)
    objects = CustomUserManager()

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"