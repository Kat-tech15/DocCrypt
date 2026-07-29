from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):


    notifications  = Notification.objects.filter(recipient=request.user).order_by("-created_at")

    return render(request, "notifications/notifications_list.html", {"notificatons": notifications})