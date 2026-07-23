from django import forms
from .models import Student

class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "programme",
            "department",
            "year_of_study",
            "status",
        ]