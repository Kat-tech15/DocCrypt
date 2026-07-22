from django.shortcuts import render
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
