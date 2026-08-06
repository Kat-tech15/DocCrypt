from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog
from django.core.paginator import Paginator
from django.db.models import Q



@login_required
def audit_logs(request):

    if not request.user.is_admin:
        return render(request, "errors/403.html", status=403)

    logs = (
        AuditLog.objects
        .select_related("user")
        .order_by("-created_at")
    )

    search = request.GET.get("search")

    if search:
        logs = logs.filter(
            Q(user__username__icontains=search) |
            Q(description__icontains=search)
        )

    action =  request.GET.get("action")

    if action:
        logs = logs.filter(action=action)

    paginator = Paginator(logs, 20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context ={
        "page_obj": page_obj,
        "search": search,
        "selected_action": action,
        "actions": AuditLog.Action.choices,
        "total_logs": AuditLog.objects.count(),
        "login_logs": AuditLog.objects.filter(action=AuditLog.Action.LOGIN).count(),
        "upload_logs": AuditLog.objects.filter(action=AuditLog.Action.UPLOAD).count(),
        "download_logs": AuditLog.objects.filter(action=AuditLog.Action.DOWNLOAD).count(),
    }

    return render(request, "logs/audit_logs.html", context)
