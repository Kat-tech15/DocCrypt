from .models import Notification

class NotificationService:

    @staticmethod
    def create_notification(
        recipient, 
        title,
        message, 
        notification_type=Notification.Type.INFO,
    ):
        Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )