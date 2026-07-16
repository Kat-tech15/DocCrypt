from django.db import transaction
from .models import CustomUser
from student.models import Student
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError


class AccountService:
    @staticmethod
    @transaction.atomic
    def create_student_account(data):
        
        temporary_password = get_random_string(
            length=10,
            allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"

        )
        if CustomUser.objects.filter(
            username=data["admission_number"]
        ).exists():
            raise ValidationError("A student with this admission number already exists.")

        if CustomUser.objects.filter(email=data["email"]).exists():
            raise ValidationError("A student with this email already exists.")
        
        user =  CustomUser.objects.create_user(
            username=data["admission_number"],
            email=data["email"],
            password=temporary_password,
            role=CustomUser.Role.STUDENT
        )
        
        student = Student.objects.create(
            user=user,
            admission_number=data["admission_number"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
            programme=data["programme"],
            department=data["department"],
            year_of_study=data["year_of_study"],
        )

        return {
            "user": user,
            "student": student,
            "temporary_password": temporary_password,
        }