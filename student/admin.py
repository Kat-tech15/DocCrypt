from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "admission_number",
        "full_name",
        "programme",
        "department",
        "year_of_study",
        "status",
    )

    list_filter = (
        "status",
        "programme",
        "department",
        "year_of_study",
    )

    search_fields = (
        "admission_number",
        "first_name",
        "last_name",
        "user__email",
    )

    ordering = (
        "admission_number",
    )

    readonly_fields = (
        "user",
    )