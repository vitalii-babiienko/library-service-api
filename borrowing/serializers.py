from django.db import transaction
from django.utils import timezone
from django_q.tasks import async_task
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.serializers import BookDetailSerializer
from borrowing.models import Borrowing
from notification.services import send_notification
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def validate_book(self, value):
        if value.inventory == 0:
            raise ValidationError(
                "Unfortunately, this book is unavailable "
                "for borrowing right now."
            )
        return value

    def validate_expected_return_date(self, value):
        if value <= timezone.now().date():
            raise ValidationError(
                "The expected return date cannot be earlier "
                "than tomorrow day."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        book = validated_data.get("book")

        if user.borrowings.filter(
            book=book,
            is_active=True,
        ).exists():
            raise ValidationError(
                "Sorry, but you have already borrowed this book!"
            )

        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(
            user=user,
            **validated_data,
        )
        message = f"{user} borrowed the book '{book.title}'."
        async_task(send_notification, message)
        return borrowing


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.CharField(
        source="book.title",
        read_only=True,
    )
    user = serializers.CharField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingReturnSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )
