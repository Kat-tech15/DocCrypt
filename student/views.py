from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Student
from django.contrib import messages
from .forms import StudentUpdateForm

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

@login_required
def edit_student(request, student_id):
    if not request.user.is_admin:
        return HttpResponseForbidden(request, "You are not authorized to access this page.")

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        form = StudentUpdateForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            messages.success(request, "Student information updated successfully.")

            return redirect("student_detail", student_id=student.id)

    else:
        form = StudentUpdateForm(instance=student)

    return render(request, "students/edit_student.html", {"form": form, "student": student})
