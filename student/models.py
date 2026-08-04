from django.db import models

from users.models import CustomUser


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DEFERRED = "DEFERRED", "Deferred"
        GRADUATED = "GRADUATED", "Graduated"
        DEACTIVATED = "DEACTIVATED", "Deactivated"

    class Year(models.IntegerChoices):
        YEAR_1 = 1 ,"Year 1"
        YEAR_2 = 2, "Year 2"
        YEAR_3 = 3, "Year 3"
        YEAR_4 = 4, "Year 4"




    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name="student")
    admission_number = models.CharField(max_length=25,unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15,blank=True)
    programme = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    year_of_study = models.IntegerField(choices=Year.choices, default=Year.YEAR_1)
    status = models.CharField(max_length=25,choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["admission_number"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"