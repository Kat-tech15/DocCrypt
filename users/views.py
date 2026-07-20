from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

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
    if not request.user.must_change_password:
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
        return render(request, "users/admin_dashboard.html")
    
    if request.user.is_student:
        return render(request, "users/student_dashboard.html")
    
    return redirect("login")

@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")