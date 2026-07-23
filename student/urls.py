from django.urls import path
from . import views

urlpatterns = [
    path("students/", views.students_list, name="student_list"),
    path("<int:student_id>/", views.student_detail, name="student_detail"),
    path("<int:student_id>/edit/", views.edit_student, name="edit_student"),
    
]