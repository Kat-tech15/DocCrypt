from django.db import transaction
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

from .models import CustomUser
from student.models import Student


class AccountService:
    """
    Handles creation and management of student accounts.
    """

    @staticmethod
    def generate_temporary_password():
        """
        Generate a secure temporary password for newly
        registered students.
        """
        return get_random_string(
            length=10,
            allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        )

    @staticmethod
    def validate_student(data):
        """
        Validate that the student's admission number and
        email are unique before creating an account.
        """
        admission_number = data["admission_number"]
        email = data["email"]

        if CustomUser.objects.filter(username=admission_number).exists():
            raise ValidationError(
                f"Admission number '{admission_number}' is already registered."
            )

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(
                f"Email '{email}' is already registered."
            )

    @staticmethod
    @transaction.atomic
    def create_student_account(data):
        """
        Creates both a CustomUser and Student record
        within a single database transaction.
        
        """

        # Validate the incoming data
        AccountService.validate_student(data)

        # Extract data once
        admission_number = data["admission_number"]
        email = data["email"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        phone_number = data["phone_number"]
        programme = data["programme"]
        department = data["department"]
        year_of_study = data["year_of_study"]

        # Generate temporary password
        temporary_password = (
            AccountService.generate_temporary_password()
        )

        # Create user account
        user = CustomUser.objects.create_user(
            username=admission_number,
            email=email,
            password=temporary_password,
            role=CustomUser.Role.STUDENT,
        )

        # Create student profile
        student = Student.objects.create(
            user=user,
            admission_number=admission_number,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            programme=programme,
            department=department,
            year_of_study=year_of_study,
        )

        return {
            "user": user,
            "student": student,
            "temporary_password": temporary_password,
        }