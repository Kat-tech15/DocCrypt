from django import forms
from student.models import Student

FORM_CONTROL = {
    "class": "form-control",
    "autocomplete": "on",
}


class StudentRegistrationForm(forms.Form):
    admission_number = forms.CharField(max_length=25,
        label="Admission Number",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Enter admission number",
            }
        ),
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Enter student email",
            }
        ),
    )

    first_name = forms.CharField(
        max_length=20,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Enter first name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=20,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Enter last name",
            }
        ),
    )

    programme = forms.CharField(
        max_length=50,
        label="Programme",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "e.g. BSc Telecommunication and IT",
            }
        ),
    )

    department = forms.CharField(
        max_length=50,
        label="Department",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "e.g. Pure and Applied Sciences",
            }
        ),
    )

    year_of_study = forms.ChoiceField(
        choices=Student.Year.choices,
        label="Year of Study",
        widget=forms.Select(
            attrs={
                **FORM_CONTROL,
                "placeholder": "e.g. 4",
            }
        ),
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "e.g. 0712345678",
            }
        ),
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Admission Number",
        widget=forms.TextInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Admission Number",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "********",
            }
        ),
    )


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Enter your new password",
            }
        ),
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                **FORM_CONTROL,
                "placeholder": "Confirm your new password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "The passwords do not match."
            )

        return cleaned_data