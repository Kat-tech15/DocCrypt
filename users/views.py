from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render, get_object_or_404
from .models import AccountActivationToken
from documents.models import Document
from student.models import Student
from django.contrib import messages
from notifications.services import NotificationService
from .forms import (
    ChangePasswordForm,
    LoginForm,
    StudentRegistrationForm,
)
from datetime import timedelta
from django.conf import settings 
from django.utils import timezone
from .services import AccountService
from logs.services import AuditService
import json
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .email_services import AccountEmailService


def home(request):
    return render(request, "users/base.html")


def register_student(request):

    if not request.user.is_admin:
        return render(request, "errors/403.html", status=403)
    
    form = StudentRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            result = AccountService.create_student_account(
                form.cleaned_data
            )
            student = result["student"]
            user = result["user"]
            activation_token = result["activation_token"]

            AuditService.register(request, student)
            AccountEmailService.send_activation_email(request, user, activation_token)

            messages.success(
                request, 
                f"student account for {student.admission_number} has been created successfully. An activation email has been sent successfully."
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
                    request, "! Your account has been deactivated. Please contact the system administrators."
                )
                return redirect("login")
            
            login(request, user)
            
            AuditService.login(request)

            #if user.is_student and user.must_change_password:
                #return redirect("change_password")

            if next_url:
                return redirect(next_url)
            
            return redirect("dashboard")

        form.add_error(None, "Invalid username or password.")


    return render(request, "users/login.html", {"form": form})


@login_required
def change_password(request):
    #if  not request.user.must_change_password:
        #return redirect("dashboard")

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

        NotificationService.password_changed(request.user)

        AuditService.password_changed(request)
        

        login(request, request.user)

        return redirect("login")
    

    return render(request, "users/change_password.html", {"form": form})


@login_required
def dashboard(request):

    if request.user.is_admin:

        total_students = Student.objects.count()

        active_students = Student.objects.filter(status=Student.Status.ACTIVE).count()
        deferred_students = Student.objects.filter(status =Student.Status.DEFERRED).count()
        graduated_students = Student.objects.filter(status=Student.Status.GRADUATED).count()
        deactivated_students = Student.objects.filter(status=Student.Status.DEACTIVATED).count()
        total_documents = Document.objects.count()
        recent_documents = Document.objects.select_related("student").order_by("-uploaded_at")[:5]
        recent_students = Student.objects.order_by("-id")[:5]
        document_uploads = (
            Student.objects.annotate(upload_count=Count("documents"))
            .values("admission_number", "upload_count")
            .order_by("-upload_count")[:10]
        )
        document_upload_chart = {
            "labels": [item["admission_number"] for item in document_uploads],
            "counts": [item["upload_count"] for item in document_uploads],
        }

        programme_distribution = (
            Student.objects
            .values("programme")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        programme_chart = {
            "labels": [item["programme"] for item in programme_distribution],
            "counts": [item["total"] for item in programme_distribution],
        }

        registrations = (
            Student.objects
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )
        regisration_chart = {
            "lables": [
                item["month"].strftime("%b %Y") for item in registrations
            ],
            "counts": [
                item["total"] for item in registrations
            ],
        }

        context = {
            "total_students": total_students,
            "active_students": active_students,
            "deferred_students": deferred_students,
            "graduated_students": graduated_students,
            "deactivated_students": deactivated_students,
            "total_documents": total_documents,
            "recent_documents": recent_documents,
            "recent_students": recent_students,

            "student_status_chart": [
                active_students,
                deferred_students,
                graduated_students,
                deactivated_students,
            ],

            "document_upload_chart": json.dumps(document_upload_chart),
            "programme_chart": json.dumps(programme_chart),
            "registration_chart": json.dumps(regisration_chart),

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
        return render(request, "errors/403.html", status=403)

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        if student.status == Student.Status.ACTIVE:
            student.status = Student.Status.DEACTIVATED

            NotificationService.account_deactivated(student)
            AuditService.account_deactivated(request, student)

            messages.info(request, f"{student.full_name} has been deactivated.")

        else:
            student.status = Student.Status.ACTIVE

            NotificationService.account_activated(student)
            AuditService.account_activated(request, student)
            
            messages.info(request, f"{student.full_name} has been activated.")

        student.save()

        return redirect("student_detail", student.id)

    return render(request, "students/toggle_student_status.html", {"student": student})

@login_required
@require_POST
def logout_view(request):

    AuditService.logout(request)
    
    logout(request)

    return redirect("login")

def activation_account(request, token):

    try:
        activation_token = get_object_or_404(
            AccountActivationToken,
            token=token
        )
    except AccountActivationToken.DoesNotExist:
        return render(
            request, "users/activation_invlaid.html",
            {
                "message": (
                    "This activation link is invalid or no longer available. "
                    "Please contact the system administrator to request anew activation link."
                )
            },
        )

    if activation_token.used:
        return render(
            request,
            "users/activation_invalid.html",
            {
                "message": (
                    "This activation link has already been used."
                )
            },
        )

    expiration_time = (
        activation_token.created_at
        + timedelta(
            hours=settings.ACCOUNT_ACTIVATION_TIMEOUT_HOURS
        )
    )

    if timezone.now() > expiration_time:
        return render(
            request,
            "users/activation_invalid.html",
            {
                "message": (
                    "This activation link has expired. "
                    "Please contact the system administrator "
                    "to request a new activation link."
                )
            },
        )

    user = activation_token.user

    if not user.must_change_password:
        return render(
            request,
            "users/activation_invalid.html",
            {
                "message": (
                    "This account has already been activated."
                )
            },
        )

    if request.method == "POST":

        form = ChangePasswordForm(request.POST)

        if form.is_valid():

            user.set_password(
                form.cleaned_data["new_password"]
            )

            user.must_change_password = False

            user.save(
                update_fields=[
                    "password",
                    "must_change_password",
                ]
            )

            # Mark the activation token as used
            activation_token.used = True
            activation_token.save(
                update_fields=["used"]
            )

            login(request, user)

            AuditService.password_changed(request)

            messages.success(
                request,
                "Your account has been activated successfully. "
                "You can now access DocCrypt."
            )

            return redirect("dashboard")

    else:
        form = ChangePasswordForm()

    return render(
        request,
        "users/activate_account.html",
        {
            "form": form,
            "user": user,
            "activation_token": activation_token,
        },
    )
    
def error_400(request, exception):
    return render(request, "errors/400.html", status=400)


def error_403(request, exception):
    return render(request, "errors/403.html", status=403)


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)