from  django.urls import path 
from . import views

urlpatterns = [
    path("notifications/", views.notification_list, name="notification_list"),
    path("mark-read/", views.mark_notifications_read, name="mark_notifications_read"),
]