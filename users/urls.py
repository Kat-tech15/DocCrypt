from django.urls import path
from . import views

urlpatterns = [
    path("register-student/", views.register_student, name="register_student"),
    path("login/", views.login_view, name="login"),
    path("change-password/", views.change_password, name="change-password"),
    path("dashboard", views.dashboard, name="dashboard"),
]