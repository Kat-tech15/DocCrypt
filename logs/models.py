from django.db import models
from users.models import CustomUser


class AuditLog(models.Model):

    class Action(models.TextChoices):
        REGISTER = "REGISTER", "Register"
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Update"

        UPLOAD = "UPLOAD", "Upload"
        DOWNLOAD = "DOWNLOAD", "Download"
        PREVIEW = "PREVIEW", "Preview"

        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Changed"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"

        ACCOUNT_ACTIVATED = "ACCOUNT_ACTIVATED", "Account Activated"
        ACCOUNT_EDITED = "ACCOUNT_EDITED", "Account Edited"
        ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED", "Account Deactivated"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=50, choices=Action.choices)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action}"