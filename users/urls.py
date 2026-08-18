from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register-student/", views.register_student, name="register_student"),
    path("login/", views.login_view, name="login"),
    path("change-password/", views.change_password, name="change_password"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("students/<int:student_id>/deactivate", views.toggle_student_status, name="toggle_student_status"),
    path("logout/", views.logout_view, name="logout"),
    path("activate/<uuid:token>/", views.activation_account, name="activation_account"),
]
