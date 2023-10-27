from rest_framework import serializers

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
