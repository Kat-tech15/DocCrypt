from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    PDF_CONTENT_TYPE = "application/pdf"

    class Meta:
        model = Document
        fields = (
            "student",
            "title",
            "original_file",
        )

        labels = {
            "title": "Document Title",
            "original_file": "Select PDF",
        }

    def clean_original_file(self):
        file = self.cleaned_data.get("original_file")

        if not file:
            return file

        if not hasattr(file, "content_type"):
            return file

        if not file.name.lower().endswith(".pdf"):
            raise forms.ValidationError(
                "Only PDF files are allowed."
            )

        if file.content_type != self.PDF_CONTENT_TYPE:
            raise forms.ValidationError(
                "Please upload a valid PDF document."
            )

        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                "Files must not exceed 10 MB."
            )

        return file

class DocumentEditForm(forms.ModelForm):
    MAX_FILE_SIZE = 10 * 1024 * 1024
    PDF_CONTENT_TYPE = "application/pdf"

    class Meta:
        model = Document
        fields = (
            "student",
            "title",
            "original_file",
        )

        labels = {
            "title": "Document Title",
            "original_file": "Replace PDF (Optional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The administrator doesn't have to upload a new file
        self.fields["original_file"].required = False

    def clean_original_file(self):
        file = self.cleaned_data.get("original_file")

        # No replacement selected
        if not file:
            return file

        if not hasattr(file, "content_type"):
            return file

        if not file.name.lower().endswith(".pdf"):
            raise forms.ValidationError(
                "Only PDF files are allowed."
            )

        if file.content_type != self.PDF_CONTENT_TYPE:
            raise forms.ValidationError(
                "Please upload a valid PDF document."
            )

        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                "Files must not exceed 10 MB."
            )

        return file