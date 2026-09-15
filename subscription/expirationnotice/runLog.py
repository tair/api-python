from subscription.models import SubscriptionExpirationNotificationLog


def record(run_date, success, message=None):
    SubscriptionExpirationNotificationLog.objects.create(
        run_date=run_date,
        success=success,
        message=message,
    )
