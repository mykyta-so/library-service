from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookListSerializer, BookSerializer
from borrowings.models import Borrowing
from django.utils import timezone

from borrowings.validators import (
    validate_book_not_already_returned,
    validate_book_availability,
    validate_non_past_return_date,
)


class ReturnBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("actual_return_date", "is_active")
        read_only_fields = ("actual_return_date", "is_active")

    def validate(self, attrs):
        validate_book_not_already_returned(
            self.instance.actual_return_date, ValidationError
        )
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.book.return_one_copy()
        instance.book.save()
        instance.actual_return_date = timezone.localdate()
        instance.is_active = False
        instance.save()
        return instance


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        )
        read_only_fields = (
            "user",
            "actual_return_date",
            "is_active",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        )
        read_only_fields = (
            "user",
            "actual_return_date",
            "is_active",
        )

    def validate(self, attrs):
        print(attrs)
        validate_book_availability(
            copies=attrs["book"].copies, error_to_raise=ValidationError
        )
        validate_non_past_return_date(
            borrow_date=timezone.localdate(),
            expected_return_date=attrs["expected_return_date"],
            error_to_raise=ValidationError,
        )
        return attrs

    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        borrowing.book.borrow_one_copy()
        borrowing.book.save()
        return borrowing
