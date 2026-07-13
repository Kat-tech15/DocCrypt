from django import forms 

class StudentRegistrationForm(forms.Form):
    admission_number = forms.CharField(max_length=25, label="Admission Number")
    email =  forms.EmailField(label="Email Address")
    first_name =  forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    programme = forms.CharField(max_length=50)
    department = forms.CharField(max_length=50)
    year_of_study = forms.IntegerField(min_value=1)
    phone_number =  forms.CharField(max_length=15, required=False)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

def clean(self):
    clean_data = super().clean()
    password = clean_data.get("new_password")
    confirm = clean_data.get("confirm_password")


    if password != confirm:
        raise forms.ValidationError("Passwords do not match.")
    
    return clean_data