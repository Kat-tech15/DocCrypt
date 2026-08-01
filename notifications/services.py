from .models import Notification
from .constants import NotificationTitles


class NotificationService:

    @staticmethod
    def create(
        *,
        recipient,
        title,
        message,
        notification_type=Notification.Type.INFO,
    ):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    @staticmethod
    def success(recipient, title, message):

        return NotificationService.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=Notification.Type.SUCCESS,
        )

    @staticmethod
    def info(recipient, title, message):

        return NotificationService.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=Notification.Type.INFO,
        )

    @staticmethod
    def warning(recipient, title, message):

        return NotificationService.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=Notification.Type.WARNING,
        )

    @staticmethod
    def error(recipient, title, message):

        return NotificationService.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=Notification.Type.ERROR,
        )

    @staticmethod
    def profile_created(user):

        NotificationService.success(
            recipient=user,
            title=NotificationTitles.PROFILE_UPDATED,
            message=(
                "Your student profile has been updated by the administator."
            ),
        )

    @staticmethod
    def document_uploaded(document, administrator):

        NotificationService.success(
            recipient=document.student.user,
            title=NotificationTitles.DOCUMENT_UPLOADED,
            message=(
                f"A new document '{document.title}' has been uploaded."
            ),

        )

        NotificationService.info(
            recipient=administrator,
            title=NotificationTitles.DOCUMENT_UPLOADED,
            message=(
                f'You uploaded "{document.title}" for '
                f'{document.student.full_name}.'
            ),
        )

    @staticmethod
    def document_updated(document):

        NotificationService.success(
            recipient=document.student.user,
            title=NotificationTitles.DOCUMENT_UPDATED,
            message=(
                f"'{document.title}' has been updated successfuly."
            ),
        )

    @staticmethod
    def document_downloaded(document):

        NotificationService.success(
            recipient=document.student.user,
            title=NotificationTitles.DOCUMENT_DOWNLOADED,
            message=(
                f'You downloaded "{document.title}".'
            ),
        )

        if document.uploaded_by:
            NotificationService.info(
                recipient=document.uploaded_by,
                title=NotificationTitles.DOCUMENT_DOWNLOADED,
                message=(
                    f'{document.student.full_name} downloaded "{document.title}".'
                ),
            )

    @staticmethod
    def document_previewed(document, administrator):

        NotificationService.info(
            recipient=administrator,
            title=NotificationTitles.DOCUMENT_PREVIEWED,
            message=(
                f'You previewed document "{document.title}" .'
                f'for {document.student.full_name}.'
            ),
        )

    @staticmethod
    def password_changed(user):

        NotificationService.success(
            recipient=user,
            title=NotificationTitles.PASSWORD_CHANGED,
            message=(
                "Your password has been changed."
            ),
        )

    @staticmethod
    def password_reset(user):

        NotificationService.warning(
            recipient=user,
            title=NotificationTitles.PASSWORD_RESET,
            message=(
                "Your password has been reset."
            ),
        )

    @staticmethod
    def account_activated(student):

        NotificationService.info(
            recipient=student.user,
            title=NotificationTitles.ACCOUNT_ACTIVATED,
            message=(
                "Your account has been activated."
            ),
        )

    @staticmethod
    def account_deactivated(student):

        NotificationService.warning(
            recipient=student.user,
            title=NotificationTitles.ACCOUNT_DEACTIVATED,
            message=(
                "Your account has been deactivated, contact the administrator to have it activated."
            ),
        )

    @staticmethod
    def profile_updated(student):

        NotificationService.success(
            recipient=student.user,
            title=NotificationTitles.PROFILE_UPDATED,
            message=(
                "Your profile has been updated."
            ),
        )
    