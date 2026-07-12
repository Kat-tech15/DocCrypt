from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import StudentRegistrationForm
from .services import AccountService


def register_student(request):

    if request.method == "POST":

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            result = AccountService.create_student_account(
                form.cleaned_data
            )

            messages.success(
                request,
                f"Student account created successfully!"
                f"Temporary Password: {result['temporary_password']}"
            )

            return redirect("register_student")

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