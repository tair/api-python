from subscription.models import SubscriptionExpirationNotificationLog


def last_success():
    latest = SubscriptionExpirationNotificationLog.objects.filter(
        success=True,
    ).order_by('-run_date').first()
    return latest.run_date if latest else None


def record(run_date, success, message=None):
    SubscriptionExpirationNotificationLog.objects.create(
        run_date=run_date,
        success=success,
        message=message,
    )
