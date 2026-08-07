from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog
from django.core.paginator import Paginator
from django.db.models import Q
import csv
import io
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)



@login_required
def audit_logs(request):

    if not request.user.is_admin:
        return render(request, "errors/403.html", status=403)

    logs = (
        AuditLog.objects
        .select_related("user")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()

    if search:
        logs = logs.filter(
            Q(user__username__icontains=search)
            | Q(action__icontains=search)
            | Q(description__icontains=search)
            | Q(ip_address__icontains=search)
        )

    action = request.GET.get("action", "").strip()

    if action:
        logs = logs.filter(action=action)

    paginator = Paginator(logs, 20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,

        "search": search,

        "selected_action": action,

        "actions": AuditLog.Action.choices,

        # Statistics
        "total_logs": AuditLog.objects.count(),

        "login_logs": AuditLog.objects.filter(
            action=AuditLog.Action.LOGIN
        ).count(),

        "upload_logs": AuditLog.objects.filter(
            action=AuditLog.Action.UPLOAD
        ).count(),

        "download_logs": AuditLog.objects.filter(
            action=AuditLog.Action.DOWNLOAD
        ).count(),
    }

    return render(request, "logs/audit_logs.html", context)

@login_required
def export_audit_logs(request):

    if not request.user.is_admin:
        return render(
            request,
            "errors/403.html",
            status=403
        )

    # Get all audit logs
    logs = (
        AuditLog.objects
        .select_related("user")
        .order_by("-created_at")
    )

    # ==============================
    # SEARCH FILTER
    # ==============================

    search = request.GET.get("search", "").strip()

    if search:
        logs = logs.filter(
            Q(user__username__icontains=search)
            | Q(action__icontains=search)
            | Q(description__icontains=search)
            | Q(ip_address__icontains=search)
        )

    # ==============================
    # ACTION FILTER
    # ==============================

    action = request.GET.get("action", "").strip()

    if action:
        logs = logs.filter(action=action)

    # ==============================
    # CREATE CSV RESPONSE
    # ==============================

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="doccrypt_audit_logs.csv"'
    )

    writer = csv.writer(response)

    # ==============================
    # CSV HEADER
    # ==============================

    writer.writerow([
        "Date",
        "User",
        "Action",
        "Description",
        "IP Address",
    ])

    # ==============================
    # CSV DATA
    # ==============================

    for log in logs:

        writer.writerow([
            log.created_at.strftime("%d/%m/%Y %H:%M")
            if log.created_at else "-",

            log.user.username
            if log.user
            else "-",

            log.get_action_display(),

            log.description
            if log.description
            else "-",

            log.ip_address
            if log.ip_address
            else "-",
        ])

    return response

@login_required
def export_audit_logs_pdf(request):

    if not request.user.is_admin:
        return render(
            request,
            "errors/403.html",
            status=403
        )

    logs = (
        AuditLog.objects
        .select_related("user")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()

    if search:
        logs = logs.filter(
            Q(user__username__icontains=search) |
            Q(description__icontains=search) |
            Q(action__icontains=search) |
            Q(ip_address__icontains=search)
        )

    action = request.GET.get("action", "").strip()

    if action:
        logs = logs.filter(action=action)

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="AuditTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        name="AuditSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=12,
    )

    table_header_style = ParagraphStyle(
        name="AuditTableHeader",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.white,
    )

    table_body_style = ParagraphStyle(
        name="AuditTableBody",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
        alignment=TA_LEFT,
    )

    elements = []

    elements.append(
        Paragraph(
            "Audit Logs",
            title_style
        )
    )

    if search and action:
        subtitle_text = (
            f"Search: {search} | "
            f"Action: {action}"
        )

    elif search:
        subtitle_text = f"Search: {search}"

    elif action:
        subtitle_text = f"Action: {action}"

    else:
        subtitle_text = "All recorded system activities"

    elements.append(
        Paragraph(
            subtitle_text,
            subtitle_style
        )
    )

    elements.append(
        Paragraph(
            f"Generated by: {request.user.username}",
            subtitle_style
        )
    )

    elements.append(Spacer(1, 5))

    table_data = [
        [
            Paragraph("Date", table_header_style),
            Paragraph("User", table_header_style),
            Paragraph("Action", table_header_style),
            Paragraph("Description", table_header_style),
            Paragraph("IP Address", table_header_style),
        ]
    ]

    for log in logs:

        username = (
            log.user.username
            if log.user
            else "-"
        )

        date_value = (
            log.created_at.strftime("%d %b %Y %H:%M")
            if log.created_at
            else "-"
        )

        action_value = log.get_action_display()

        description_value = (
            log.description
            if log.description
            else "-"
        )

        ip_value = (
            log.ip_address
            if log.ip_address
            else "-"
        )

        table_data.append(
            [
                Paragraph(
                    date_value,
                    table_body_style
                ),

                Paragraph(
                    username,
                    table_body_style
                ),

                Paragraph(
                    action_value,
                    table_body_style
                ),

                Paragraph(
                    description_value,
                    table_body_style
                ),

                Paragraph(
                    ip_value,
                    table_body_style
                ),
            ]
        )

    if len(table_data) == 1:

        table_data.append(
            [
                Paragraph(
                    "No audit logs found.",
                    table_body_style
                ),
                "",
                "",
                "",
                "",
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            32 * mm,
            42 * mm,
            32 * mm,
            125 * mm,
            35 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, 0),
                    "CENTER",
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),

                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f3f4f6"),
                    ],
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    elements.append(table)
    document.build(elements)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="audit_logs.pdf"'

    return response