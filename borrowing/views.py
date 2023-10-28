from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)


@extend_schema(tags=["Borrowings"])
class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "book",
                "user",
            )

        if self.action == "list":
            user_id = self.request.query_params.get("user_id")
            is_active = self.request.query_params.get("is_active")

            if user_id:
                queryset = queryset.filter(user_id=user_id)

            if is_active:
                queryset = queryset.filter(is_active=is_active.capitalize())

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_borrowing(self, request, pk=None):
        """Endpoint for returning the book to the library"""
        borrowing = get_object_or_404(
            Borrowing,
            user=request.user,
            pk=pk,
        )

        if borrowing.is_active:
            borrowing.actual_return_date = timezone.now().date()
            borrowing.is_active = False
            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

            return Response(
                {"success": "You have successfully returned the book."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "You have already returned the book!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=int,
                description="Filter by user id (ex. ?user_id=1)",
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                type=bool,
                description="Filter by borrowing status (ex. ?is_active=true)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
