from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.serializers import BookDetailSerializer
from borrowing.models import Borrowing
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

    def validate(self, data):
        user = self.context["request"].user
        data["user"] = user
        return data

    def validate_book(self, value):
        if value.inventory == 0:
            raise ValidationError(
                "Unfortunately, this book is unavailable "
                "for borrowing right now."
            )
        value.inventory -= 1
        value.save()

        return value

    def validate_expected_return_date(self, value):
        if value <= timezone.now().date():
            raise ValidationError(
                "The expected return date cannot be earlier "
                "than tomorrow day."
            )
        return value


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
