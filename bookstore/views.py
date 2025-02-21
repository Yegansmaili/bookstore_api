from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Book

from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import *


class BookViewSet(ModelViewSet):
    # queryset = Book.objects.select_related('genre').all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddBookSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UpdateBookSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = Book.objects.select_related('genre').all()
        genre_slug = self.kwargs.get('genre_pk')
        if genre_slug is not None:
            queryset = queryset.filter(genre__slug=genre_slug).all()
        return queryset

    def create(self, request, *args, **kwargs):
        create_book_serializer = AddBookSerializer(data=request.data)
        create_book_serializer.is_valid(raise_exception=True)
        created_book = create_book_serializer.save()
        serializer = BookSerializer(created_book)
        return Response(serializer.data)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related('book').all()
        book_slug = self.kwargs.get('book_pk')
        if book_slug is not None:
            queryset = queryset.filter(book__slug=book_slug).all()
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddReviewSerializer
        return ReviewSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def create(self, request, *args, **kwargs):
        create_review_serializer = AddReviewSerializer(data=request.data,
                                                       context={'user_id': self.request.user.id})
        create_review_serializer.is_valid(raise_exception=True)
        created_review = create_review_serializer.save()
        serializer = ReviewSerializer(created_review)
        return Response(serializer.data)
