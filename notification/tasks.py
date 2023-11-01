import os

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()

from django_q.tasks import async_task

from notification.services import send_notification
from borrowing.models import Borrowing


def send_borrowings_list_notification():
    borrowings = Borrowing.objects.filter(
        is_active=True,
        expected_return_date__lt=timezone.now().date(),
    )

    if borrowings:
        borrowers = {borrowing.user.email: [] for borrowing in borrowings}

        for borrowing in borrowings:
            borrowers[borrowing.user.email].append(borrowing.book.title)

        data = [
            f"\n{email} still has not returned the books: {', '.join(titles)}."
            for email, titles in borrowers.items()
        ]
        message = "".join(data)
        async_task(send_notification, message)
    else:
        message = "No borrowings are overdue today!"
        async_task(send_notification, message)
