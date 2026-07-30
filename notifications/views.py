from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import JsonResponse


@login_required
def notification_list(request):


    all_notifications  = Notification.objects.filter(recipient=request.user).order_by("-created_at")

    return render(request, "notifications/notifications_list.html", {"notifications": all_notifications})

@login_required
def mark_notifications_read(request):

    Notification.objects.filter(recipient=request.user,
                                is_read=False,
                                ).update(is_read=True)

    return JsonResponse({"success": True})
    