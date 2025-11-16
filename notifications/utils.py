from .models import Notification

def notify_user(user, title, message, type="system", cooperative=None):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type,
        cooperative=cooperative,
    )


def notify_cooperative(cooperative, title, message, type="coop"):
    for member in cooperative.memberships.all():
        Notification.objects.create(
            user=member.user,
            title=title,
            message=message,
            type=type,
            cooperative=cooperative,
        )



