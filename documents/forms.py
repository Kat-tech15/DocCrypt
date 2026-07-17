from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "student",
            "title",
            "original_file",
        ]
    def clean_original_file(self):
        file = self.cleaned_data["original_file"]

        if not file.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        
        if file.content_type != "application/pdf":
            raise forms.ValidationError("Invalid PDF file.")
        
        return file