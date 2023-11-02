from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer, BorrowingDetailSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")
PAGINATION_COUNT = 10
NUMBER_OF_BOOKS = 10


def create_books():
    return [
        Book.objects.create(
            title=f"Title {i}",
            author=f"Author {i}",
            cover="HARD",
            inventory=5 + i,
            daily_fee=f"{5.99 + i}",
        )
        for i in range(NUMBER_OF_BOOKS)
    ]


def create_borrowings(user, books):
    return [
        Borrowing.objects.create(
            expected_return_date=timezone.now().date() + timedelta(days=2),
            book=books[i],
            user=user,
        )
        for i in range(NUMBER_OF_BOOKS)
    ]


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_borrowing_url(borrowing_id):
    return reverse("borrowing:borrowing-return-borrowing", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_pass",
        )
        self.client.force_authenticate(self.user)
        self.books = create_books()

    def test_list_borrowings(self):
        create_borrowings(self.user, self.books)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

        for i in range(PAGINATION_COUNT):
            for key in serializer.data[i]:
                self.assertEquals(
                    res.data["results"][i][key],
                    serializer.data[i][key],
                )

    def test_retrieve_borrowing_detail(self):
        create_borrowings(self.user, self.books)

        borrowing = Borrowing.objects.all()[0]

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_create_borrowing(self):
        book = self.books[0]

        payload = {
            "expected_return_date": str(timezone.now().date() + timedelta(days=2)),
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        book.refresh_from_db()

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertEquals(book, getattr(borrowing, "book"))
        self.assertEquals(book.inventory, 4)

    def test_update_borrowing_is_not_allowed(self):
        create_borrowings(self.user, self.books)

        borrowing = Borrowing.objects.all()[0]

        payload = {
            "expected_return_date": str(timezone.now().date() + timedelta(days=3)),
        }

        url = detail_url(borrowing.id)
        res = self.client.patch(url, payload)

        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_is_not_allowed(self):
        create_borrowings(self.user, self.books)

        borrowing = Borrowing.objects.all()[0]

        url = detail_url(borrowing.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_return_borrowing(self):
        self.test_create_borrowing()
        book = self.books[0]

        borrowing = Borrowing.objects.all()[0]

        url = return_borrowing_url(borrowing.id)
        res = self.client.patch(url)
        book.refresh_from_db()

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(book.inventory, 5)
