import os.path
import tempfile
from decimal import Decimal

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import (
    BookListSerializer,
    BookDetailSerializer,
)

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "Test Title",
        "author": "Test Author",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": "5.99",
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


def image_upload_url(book_id):
    return reverse("book:book-upload-image", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.book = sample_book()

    def test_list_books(self):
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data["results"], serializer.data)

    def test_retrieve_book_detail(self):
        url = detail_url(self.book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(self.book)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_create_book_unauthorized(self):
        payload = {
            "title": "Test Title",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 5.99,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_pass",
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_create_book_forbidden(self):
        payload = {
            "title": "Test Title",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 5.99,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        payload = {
            "title": "Updated Title",
        }

        url = detail_url(self.book.id)
        res = self.client.patch(url, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        url = detail_url(self.book.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "test_pass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_create_book(self):
        payload = {
            "title": "Test Title",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "5.99",
        }
        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key != "daily_fee":
                self.assertEquals(payload[key], getattr(book, key))
            else:
                self.assertEquals(Decimal("5.99"), getattr(book, key))

    def test_update_book(self):
        payload = {
            "title": "Updated Title",
        }

        url = detail_url(self.book.id)
        res = self.client.patch(url, payload)
        book = Book.objects.get(id=res.data["id"])

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(payload["title"], book.title)

    def test_delete_book(self):
        url = detail_url(self.book.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id))


class BookImageUploadTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "test_pass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def tearDown(self) -> None:
        self.book.image.delete()

    def test_upload_image_to_book(self):
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.book.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.book.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
