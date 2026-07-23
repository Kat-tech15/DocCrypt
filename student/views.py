from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Student

@login_required
def students_list(request):
    if not request.user.is_admin:
        return HttpResponseForbidden("Only administrators can access this page.")
    
    students = Student.objects.select_related("user").all()

    context ={"students": students}

    return render(request, "students/student_list.html", context)

@login_required
def student_detail(request, student_id):
    
    if not request.user.is_admin:
        return HttpResponseForbidden("This page is accessible to administrators only.")
    
    student = get_object_or_404(
        Student.objects.select_related("user"), pk=student_id
    )

    documents = student.documents.all()
    context = {
        "student": student,
        "documents": documents,
    }

    return render(request, "students/student_detail.html", context)
    