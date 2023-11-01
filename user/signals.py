from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_q.models import Schedule
from django_q.tasks import schedule


@receiver(post_migrate)
def create_schedules(sender, **kwargs):
    if sender.name == "user":
        if not Schedule.objects.filter(name="borrowings list").exists():
            schedule(
                func="notification.tasks.send_borrowings_list_notification",
                name="borrowings list",
                repeats=-1,
                schedule_type=Schedule.DAILY,
            )
