from django.db import models
from users.models import CustomUser


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=25, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    programme = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    year_of_study = models.IntegerField(default=1)
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DEFERRED = "DEFERRED", "Deferred"
        GRADUATED =  "GRADUATED", "Graduated"
    
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.ACTIVE)
    

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"