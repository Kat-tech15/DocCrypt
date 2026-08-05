from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Student
from django.contrib import messages
from .forms import StudentUpdateForm
from django.db.models import Q
from django.core.paginator import Paginator
from notifications.services import NotificationService

@login_required
def students_list(request):
    if not request.user.is_admin:
        return render(request, "errors/403.html", status=403)

    students = Student.objects.select_related("user").all().order_by("admission_number")

    query = request.GET.get("q", "")

    if query:
        students = students.filter(
            Q(admission_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(programme__icontains=query) |
            Q(department__icontains=query) |
            Q(status__icontains=query)
        )

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")

    students = paginator.get_page(page_number)

    context ={"students": students, "query": query}

    return render(request, "students/student_list.html", context)

@login_required
def student_detail(request, student_id):
    
    if not request.user.is_admin:
        return render(request, "errors/403.html", status=403)
    
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
        return render(request, "errors/403.html", status=403)

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        form = StudentUpdateForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            messages.info(request, "Student information updated successfully.")

            return redirect("student_detail", student_id=student.id)

    else:
        form = StudentUpdateForm(instance=student)

    NotificationService.profile_updated(student)

    return render(request, "students/edit_student.html", {"form": form, "student": student})
