from .models import AuditLog

class AuditService:

    @staticmethod
    def log(
        *,
        request,
        user,
        action,
        description,
    ):
        return AuditLog.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

    @staticmethod
    def register(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.REGISTER,
            description=f"Registered {request.get_user.admission_number}.",
        )

    @staticmethod
    def login(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.LOGIN,
            description="Logged into the system.",
        )

    @staticmethod
    def logout(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.LOGOUT,
            description="Logged out of the system.",
        )

    @staticmethod
    def account_activated(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.ACCOUNT_ACTIVATED,
            description=f"Activated account for {request.user.admission_number}",
        )

    @staticmethod
    def account_edited(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.ACCOUNT_EDITED,
            description=f"Edited profile for {request.user.admission_number}.",
        )

    @staticmethod
    def account_deactivated(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.ACCOUNT_DEACTIVATED,
            description=f"Deactivated account for {request.user.admission_number}",
        )

    @staticmethod
    def document_uploaded(request, document):
    
        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.UPLOAD,
            description=(
                f'Uploaded "{document.title}"'
                f'for {document.student.admission_number}.'
            ),
        )

    @staticmethod
    def document_updated(request, document):

        AuditService.log(
            request=request, 
            user=request.user,
            action=AuditLog.Action.UPDATE,
            description=f'Updated document "{document.title}" for {document.student.admission_number}.'
        )

    @staticmethod
    def document_previewed(request, document):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.PREVIEW,
            description=(
                f'Previewed "{document.title}" for {document.student.admission_number}'
            ),
        )

    @staticmethod
    def document_downloaded(request, document):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.DOWNLOAD,
            description=(
                f'Downloaded "{document.title}".'
            ),
        )

    @staticmethod
    def password_changed(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.PASSWORD_CHANGE,
            description="Passord changed.",
        )

    @staticmethod
    def password_reset(request):

        AuditService.log(
            request=request,
            user=request.user,
            action=AuditLog.Action.PASSWORD_RESET,
            description="Password reset.",
        )

    