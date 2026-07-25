from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden
from documents.models import Document
from student.models import Student
from django.contrib import messages

from .forms import (
    ChangePasswordForm,
    LoginForm,
    StudentRegistrationForm,
)
from .services import AccountService


def home(request):
    return render(request, "users/base.html")


def register_student(request):
    
    form = StudentRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            result = AccountService.create_student_account(
                form.cleaned_data
            )

            return render(
                request,
                "users/account_created.html",
                {
                    "student": result["student"],
                    "user": result["user"],
                    "temporary_password": result["temporary_password"],
                },
            )

        except ValidationError as e:
            form.add_error(None, e.message)

    return render(request, "users/register_student.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    next_url = request.GET.get("next")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        if user:
            if (user.is_student and user.student.status == user.student.Status.DEACTIVATED):

                messages.error(
                    request, "Your account has been deactivated. Please contact the system administrators."
                )
                return redirect("login")
            
            login(request, user)

            if user.is_student and user.must_change_password:
                return redirect("change_password")

            if next_url:
                return redirect(next_url)
            
            return redirect("dashboard")

        form.add_error(None, "Invalid username or password.")

    return render(request, "users/login.html", {"form": form})


@login_required
def change_password(request):
    if  not request.user.must_change_password:
        return redirect("dashboard")

    form = ChangePasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        request.user.set_password(
            form.cleaned_data["new_password"]
        )

        request.user.must_change_password = False

        request.user.save(
            update_fields=[
                "password",
                "must_change_password",
            ]
        )

        login(request, request.user)

        return redirect("dashboard")

    return render(request, "users/change_password.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.is_admin:
        
        total_students = Student.objects.count()

        active_students = Student.objects.filter(status=Student.Status.ACTIVE).count()
        deferred_students = Student.objects.filter(status =Student.Status.DEFERRED).count()
        graduated_students = Student.objects.filter(status=Student.Status.GRADUATED)
        total_documents = Document.objects.count()
        encrypted_documents = Document.objects.filter(status=Document.Status.ENCRYPTED).count()
        recent_documents = Document.objects.select_related("student").order_by("-uploaded_at")[:5]
        recent_students = Student.objects.order_by("-id")[:5]

        context = {
            "total_students": total_students,
            "active_students": active_students,
            "deferred_students": deferred_students,
            "graduated_students": graduated_students,
            "total_documents": total_documents,
            "encrypted_documents": encrypted_documents,
            "recent_documents": recent_documents,
            "recent_students": recent_students,

        }
        return render(request, "users/admin_dashboard.html", context)
    
    if request.user.is_student:

        student =request.user.student
        documents = (Document.objects.filter(student=student).order_by("-uploaded_at"))  
        encrypted_documents = documents.filter(status=Document.Status.ENCRYPTED)
                     
        

        context = {
            "student": student,
            "documents": documents[:5],
            "document_count": documents.count(),
            "encrypted_count": encrypted_documents.count(),
        }

        return render(request, "users/student_dashboard.html", context)

    
    return redirect("login")

@login_required
def toggle_student_status(request, student_id):
    if not request.user.is_admin:
        return HttpResponseForbidden(request, "Only administrators can access this service.")

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        if student.status == Student.Status.ACTIVE:
            student.status = Student.Status.DEACTIVATED
           

            messages.success(request, f"{student.full_name} has been deactivated.")

        else:
            student.status = Student.Status.ACTIVE
            messages.success(request, f"{student.full_name} has been activated.")

        student.save()

        return redirect("student_detail", student.id)

    return render(request, "students/toggle_student_status.html", {"student": student})

@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")