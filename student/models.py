from django.db import models

from users.models import CustomUser


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DEFERRED = "DEFERRED", "Deferred"
        GRADUATED = "GRADUATED", "Graduated"

    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name="student")
    admission_number = models.CharField(max_length=25,unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15,blank=True)
    programme = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    year_of_study = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=25,choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["admission_number"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"