
def unread_job_notification_count(request):
    if request.user.is_authenticated:
        return {
            "unread_job_notification_count": (
                request.user.job_notifications.filter(
                    is_read=False
                ).count()
            )
        }

    return {
        "unread_job_notification_count": 0
    }
