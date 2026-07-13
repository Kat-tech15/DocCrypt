from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required

from .forms import StudentRegistrationForm, LoginForm, ChangePasswordForm
from .services import AccountService


def register_student(request):

    if request.method == "POST":

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            result = AccountService.create_student_account(
                form.cleaned_data
            )
            
            context = {
                "student": result["student"],
                "user": result["user"],
                "temporary_password": result["temporary_password"],
            }
    
            return render(request, "users/account_created.html", context)

    else:

        form = StudentRegistrationForm()

    context = {
        "form": form
    }

    return render(
        request,
        "users/register_student.html",
        context
    )

def login_view(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.must_change_password:
                    return redirect("change-password")

                return redirect("dashboard")
            
            form.add_error(
                None,
                "Invalid username or password."
            )
    return render(request, "users/login.html", {"form": form})

@login_required
def change_password(request):
    if not request.user.must_change_password:
        return redirect("dashboard")
    
    form = ChangePasswordForm()
    if request.method == "POST":
        form =ChangePasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(
                form.cleaned_data["new_password"]
            )
            request.user.must_change_password = False
            request.user.save()
            login(request, request.user)
            return redirect("dashboard")
        
    return render(request, "users/change_password.html", {"form": form})
    

@login_required
def dashboard(request):
    return render(request, "users/dashboard.html")