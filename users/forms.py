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